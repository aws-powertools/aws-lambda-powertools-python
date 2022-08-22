import json
import logging
import sys
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple, Type
from uuid import uuid4

import boto3
import pytest
import yaml
from aws_cdk import App, AssetStaging, BundlingOptions, CfnOutput, DockerImage, RemovalPolicy, Stack, aws_logs
from aws_cdk.aws_lambda import Code, Function, LayerVersion, Runtime, Tracing
from filelock import FileLock
from mypy_boto3_cloudformation import CloudFormationClient

from tests.e2e.utils.asset import Assets

PYTHON_RUNTIME_VERSION = f"V{''.join(map(str, sys.version_info[:2]))}"

logger = logging.getLogger(__name__)


class BaseInfrastructureStack(ABC):
    @abstractmethod
    def synthesize(self) -> Tuple[dict, str]:
        ...

    @abstractmethod
    def __call__(self) -> Tuple[dict, str]:
        ...


class PythonVersion(Enum):
    V37 = {"runtime": Runtime.PYTHON_3_7, "image": Runtime.PYTHON_3_7.bundling_image.image}
    V38 = {"runtime": Runtime.PYTHON_3_8, "image": Runtime.PYTHON_3_8.bundling_image.image}
    V39 = {"runtime": Runtime.PYTHON_3_9, "image": Runtime.PYTHON_3_9.bundling_image.image}


class BaseInfrastructure(ABC):
    def __init__(self, feature_name: str, handlers_dir: Path, layer_arn: str = "") -> None:
        self.feature_name = feature_name
        self.stack_name = f"test-{feature_name}-{uuid4()}"
        self.handlers_dir = handlers_dir
        self.layer_arn = layer_arn
        self.stack_outputs: Dict[str, str] = {}

        # NOTE: Investigate why cdk.Environment in Stack
        # changes synthesized asset (no object_key in asset manifest)
        self.app = App()
        self.stack = Stack(self.app, self.stack_name)
        self.session = boto3.Session()
        self.cfn: CloudFormationClient = self.session.client("cloudformation")

        # NOTE: CDK stack account and region are tokens, we need to resolve earlier
        self.account_id = self.session.client("sts").get_caller_identity()["Account"]
        self.region = self.session.region_name

    def create_lambda_functions(self, function_props: Optional[Dict] = None):
        """Create Lambda functions available under handlers_dir

        It creates CloudFormation Outputs for every function found in PascalCase. For example,
        {handlers_dir}/basic_handler.py creates `BasicHandler` and `BasicHandlerArn` outputs.


        Parameters
        ----------
        function_props: Optional[Dict]
            Dictionary representing CDK Lambda FunctionProps to override defaults

        Examples
        --------

        Creating Lambda functions available in the handlers directory

        ```python
        self.create_lambda_functions()
        ```

        Creating Lambda functions and override runtime to Python 3.7

        ```python
        from aws_cdk.aws_lambda import Runtime

        self.create_lambda_functions(function_props={"runtime": Runtime.PYTHON_3_7)
        ```
        """
        handlers = list(self.handlers_dir.rglob("*.py"))
        source = Code.from_asset(f"{self.handlers_dir}")
        logger.debug(f"Creating functions for handlers: {handlers}")
        if not self.layer_arn:
            raise ValueError(
                """Lambda Layer ARN cannot be empty when creating Lambda functions.
                Make sure to inject `lambda_layer_arn` fixture and pass at the constructor level"""
            )

        layer = LayerVersion.from_layer_version_arn(self.stack, "layer-arn", layer_version_arn=self.layer_arn)
        function_settings_override = function_props or {}
        for fn in handlers:
            fn_name = fn.stem
            fn_name_pascal_case = fn_name.title().replace("_", "")  # basic_handler -> BasicHandler
            logger.debug(f"Creating function: {fn_name_pascal_case}")
            function_settings = {
                "id": f"{fn_name}-lambda",
                "code": source,
                "handler": f"{fn_name}.lambda_handler",
                "tracing": Tracing.ACTIVE,
                "runtime": Runtime.PYTHON_3_9,
                "layers": [layer],
                **function_settings_override,
            }

            function = Function(self.stack, **function_settings)

            aws_logs.LogGroup(
                self.stack,
                id=f"{fn_name}-lg",
                log_group_name=f"/aws/lambda/{function.function_name}",
                retention=aws_logs.RetentionDays.ONE_DAY,
                removal_policy=RemovalPolicy.DESTROY,
            )

            # CFN Outputs only support hyphen hence pascal case
            self.add_cfn_output(name=fn_name_pascal_case, value=function.function_name, arn=function.function_arn)

    def deploy(self) -> Dict[str, str]:
        """Creates CloudFormation Stack and return stack outputs as dict

        Returns
        -------
        Dict[str, str]
            CloudFormation Stack Outputs with output key and value
        """
        template, asset_manifest_file = self._synthesize()
        assets = Assets(asset_manifest=asset_manifest_file, account_id=self.account_id, region=self.region)
        assets.upload()
        self.stack_outputs = self._deploy_stack(self.stack_name, template)
        return self.stack_outputs

    def delete(self) -> None:
        """Delete CloudFormation Stack"""
        logger.debug(f"Deleting stack: {self.stack_name}")
        self.cfn.delete_stack(StackName=self.stack_name)

    @abstractmethod
    def create_resources(self) -> None:
        """Create any necessary CDK resources. It'll be called before deploy

        Examples
        -------

        Creating a S3 bucket and export name and ARN

        ```python
        def created_resources(self):
            s3 = s3.Bucket(self.stack, "MyBucket")

            # This will create MyBucket and MyBucketArn CloudFormation Output
            self.add_cfn_output(name="MyBucket", value=s3.bucket_name, arn_value=bucket.bucket_arn)
        ```

        Creating Lambda functions available in the handlers directory

        ```python
        def created_resources(self):
            self.create_lambda_functions()
        ```
        """
        ...

    def _synthesize(self) -> Tuple[Dict, Path]:
        logger.debug("Creating CDK Stack resources")
        self.create_resources()
        logger.debug("Synthesizing CDK Stack into raw CloudFormation template")
        cloud_assembly = self.app.synth()
        cf_template: Dict = cloud_assembly.get_stack_by_name(self.stack_name).template
        cloud_assembly_assets_manifest_path: str = (
            cloud_assembly.get_stack_by_name(self.stack_name).dependencies[0].file  # type: ignore[attr-defined]
        )
        return cf_template, Path(cloud_assembly_assets_manifest_path)

    def _deploy_stack(self, stack_name: str, template: Dict) -> Dict[str, str]:
        logger.debug(f"Creating CloudFormation Stack: {stack_name}")
        self.cfn.create_stack(
            StackName=stack_name,
            TemplateBody=yaml.dump(template),
            TimeoutInMinutes=10,
            OnFailure="ROLLBACK",
            Capabilities=["CAPABILITY_IAM"],
        )
        waiter = self.cfn.get_waiter("stack_create_complete")
        waiter.wait(StackName=stack_name, WaiterConfig={"Delay": 10, "MaxAttempts": 50})

        stack_details = self.cfn.describe_stacks(StackName=stack_name)
        stack_outputs = stack_details["Stacks"][0]["Outputs"]
        return {output["OutputKey"]: output["OutputValue"] for output in stack_outputs if output["OutputKey"]}

    def add_cfn_output(self, name: str, value: str, arn: str = ""):
        """Create {Name} and optionally {Name}Arn CloudFormation Outputs.

        Parameters
        ----------
        name : str
            CloudFormation Output Key
        value : str
            CloudFormation Output Value
        arn : str
            CloudFormation Output Value for ARN
        """
        CfnOutput(self.stack, f"{name}", value=value)
        if arn:
            CfnOutput(self.stack, f"{name}Arn", value=arn)


def deploy_once(
    stack: Type[BaseInfrastructure],
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
    worker_id: str,
    layer_arn: str,
) -> Generator[Dict[str, str], None, None]:
    """Deploys provided stack once whether CPU parallelization is enabled or not

    Parameters
    ----------
    stack : Type[BaseInfrastructure]
        stack class to instantiate and deploy, for example MetricStack.
        Not to be confused with class instance (MetricStack()).
    request : pytest.FixtureRequest
        pytest request fixture to introspect absolute path to test being executed
    tmp_path_factory : pytest.TempPathFactory
        pytest temporary path factory to discover shared tmp when multiple CPU processes are spun up
    worker_id : str
        pytest-xdist worker identification to detect whether parallelization is enabled

    Yields
    ------
    Generator[Dict[str, str], None, None]
        stack CloudFormation outputs
    """
    handlers_dir = f"{request.node.path.parent}/handlers"
    stack = stack(handlers_dir=Path(handlers_dir), layer_arn=layer_arn)

    try:
        if worker_id == "master":
            # no parallelization, deploy stack and let fixture be cached
            yield stack.deploy()
        else:
            # tmp dir shared by all workers
            root_tmp_dir = tmp_path_factory.getbasetemp().parent
            cache = root_tmp_dir / "cache.json"

            with FileLock(f"{cache}.lock"):
                # If cache exists, return stack outputs back
                # otherwise it's the first run by the main worker
                # deploy and return stack outputs so subsequent workers can reuse
                if cache.is_file():
                    stack_outputs = json.loads(cache.read_text())
                else:
                    stack_outputs: Dict = stack.deploy()
                    cache.write_text(json.dumps(stack_outputs))
            yield stack_outputs
    finally:
        stack.delete()


class LambdaLayerStack(BaseInfrastructure):
    FEATURE_NAME = "lambda-layer"

    def __init__(self, handlers_dir: Path, feature_name: str = FEATURE_NAME, layer_arn: str = "") -> None:
        super().__init__(feature_name, handlers_dir, layer_arn)

    def create_resources(self):
        layer = self._create_layer()
        CfnOutput(self.stack, "LayerArn", value=layer)

    def _create_layer(self) -> str:
        logger.debug("Creating Lambda Layer with latest source code available")
        output_dir = Path(str(AssetStaging.BUNDLING_OUTPUT_DIR), "python")
        input_dir = Path(str(AssetStaging.BUNDLING_INPUT_DIR), "aws_lambda_powertools")

        build_commands = [f"pip install .[pydantic] -t {output_dir}", f"cp -R {input_dir} {output_dir}"]
        layer = LayerVersion(
            self.stack,
            "aws-lambda-powertools-e2e-test",
            layer_version_name="aws-lambda-powertools-e2e-test",
            compatible_runtimes=[PythonVersion[PYTHON_RUNTIME_VERSION].value["runtime"]],
            code=Code.from_asset(
                path=".",
                bundling=BundlingOptions(
                    image=DockerImage.from_build(
                        str(Path(__file__).parent),
                        build_args={"IMAGE": PythonVersion[PYTHON_RUNTIME_VERSION].value["image"]},
                    ),
                    command=["bash", "-c", " && ".join(build_commands)],
                ),
            ),
        )
        return layer.layer_version_arn
