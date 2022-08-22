from pathlib import Path

from tests.e2e.utils.infrastructure import BaseInfrastructureV2


class MetricsStack(BaseInfrastructureV2):
    FEATURE_NAME = "metrics"

    def __init__(self, handlers_dir: Path, feature_name: str = FEATURE_NAME, layer_arn: str = "") -> None:
        super().__init__(feature_name, handlers_dir, layer_arn)

    def create_resources(self):
        self.create_lambda_functions()
