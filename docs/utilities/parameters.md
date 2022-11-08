---
title: Parameters
description: Utility
---

<!-- markdownlint-disable MD013 -->
The parameters utility provides high-level functions to retrieve one or multiple parameter values from [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html){target="_blank"}, [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/){target="_blank"}, [AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html){target="_blank"}, [Amazon DynamoDB](https://aws.amazon.com/dynamodb/){target="_blank"}, or bring your own.

## Key features

* Retrieve one or multiple parameters from the underlying provider
* Cache parameter values for a given amount of time (defaults to 5 seconds)
* Transform parameter values from JSON or base 64 encoded strings
* Bring Your Own Parameter Store Provider

## Getting started

By default, we fetch parameters from System Manager Parameter Store, secrets from Secrets Manager, and application configuration from AppConfig.

### IAM Permissions

This utility requires additional permissions to work as expected.

???+ note
    Different parameter providers require different permissions.

| Provider  | Function/Method                                                        | IAM Permission                                                                       |
| --------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| SSM       | **`get_parameter`**, **`SSMProvider.get`**                             | **`ssm:GetParameter`**                                                               |
| SSM       | **`get_parameters`**, **`SSMProvider.get_multiple`**                   | **`ssm:GetParametersByPath`**                                                        |
| SSM       | **`get_parameters_by_name`**, **`SSMProvider.get_parameters_by_name`** | **`ssm:GetParameter`** and **`ssm:GetParameters`**                                   |
| SSM       | If using **`decrypt=True`**                                            | You must add an additional permission **`kms:Decrypt`**                              |
| Secrets   | **`get_secret`**, **`SecretsManager.get`**                             | **`secretsmanager:GetSecretValue`**                                                  |
| DynamoDB  | **`DynamoDBProvider.get`**                                             | **`dynamodb:GetItem`**                                                               |
| DynamoDB  | **`DynamoDBProvider.get_multiple`**                                    | **`dynamodb:Query`**                                                                 |
| AppConfig | **`get_app_config`**, **`AppConfigProvider.get_app_config`**           | **`appconfig:GetLatestConfiguration`** and **`appconfig:StartConfigurationSession`** |

### Fetching parameters

You can retrieve a single parameter  using `get_parameter` high-level function.

```python hl_lines="5" title="Fetching a single parameter"
from aws_lambda_powertools.utilities import parameters

def handler(event, context):
	# Retrieve a single parameter
	value = parameters.get_parameter("/my/parameter")

```

For multiple parameters, you can use either:

* `get_parameters` to recursively fetch all parameters by path.
* `get_parameters_by_name` to fetch distinct parameters by their full name. It also accepts custom caching, transform, decrypt per parameter.

=== "get_parameters"

    ```python hl_lines="1 6"
    from aws_lambda_powertools.utilities import parameters

    def handler(event, context):
    	# Retrieve multiple parameters from a path prefix recursively
    	# This returns a dict with the parameter name as key
    	values = parameters.get_parameters("/my/path/prefix")
    	for parameter, value in values.items():
    		print(f"{parameter}: {value}")
    ```

=== "get_parameters_by_name"

    ```python hl_lines="3 5 14"
	from typing import Any

    from aws_lambda_powertools.utilities import get_parameters_by_name

	parameters = {
      "/develop/service/commons/telemetry/config": {"max_age": 300, "transform": "json"},
      "/no_cache_param": {"max_age": 0},
      # inherit default values
	  "/develop/service/payment/api/capture/url": {},
	}

    def handler(event, context):
    	# This returns a dict with the parameter name as key
    	response: dict[str, Any] = parameters.get_parameters_by_name(parameters=parameters, max_age=60)
    	for parameter, value in response.items():
    		print(f"{parameter}: {value}")
    ```

???+ tip "`get_parameters_by_name` supports graceful error handling"
	By default, we will raise `GetParameterError` when any parameter fails to be fetched. You can override it by setting `raise_on_error=False`.

	When disabled, we take the following actions:

	* Add failed parameter name in the `_errors` key, _e.g._, `{_errors: ["/param1", "/param2"]}`
	* Keep only successful parameter names and their values in the response
	* Raise `GetParameterError` if any of your parameters is named `_errors`

```python hl_lines="3 5 12-13 15" title="Graceful error handling"
from typing import Any

from aws_lambda_powertools.utilities import get_parameters_by_name

parameters = {
  "/develop/service/commons/telemetry/config": {"max_age": 300, "transform": "json"},
  # it would fail by default
  "/this/param/does/not/exist"
}

def handler(event, context):
	values: dict[str, Any] = parameters.get_parameters_by_name(parameters=parameters, raise_on_error=False)
	errors: list[str] = values.get("_errors", [])

    # Handle gracefully, since '/this/param/does/not/exist' will only be available in `_errors`
	if errors:
		...

	for parameter, value in values.items():
		print(f"{parameter}: {value}")
```

### Fetching secrets

You can fetch secrets stored in Secrets Manager using `get_secrets`.

```python hl_lines="1 5" title="Fetching secrets"
from aws_lambda_powertools.utilities import parameters

def handler(event, context):
	# Retrieve a single secret
	value = parameters.get_secret("my-secret")
```

### Fetching app configurations

You can fetch application configurations in AWS AppConfig using `get_app_config`.

The following will retrieve the latest version and store it in the cache.

```python hl_lines="1 5" title="Fetching latest config from AppConfig"
from aws_lambda_powertools.utilities import parameters

def handler(event, context):
	# Retrieve a single configuration, latest version
	value: bytes = parameters.get_app_config(name="my_configuration", environment="my_env", application="my_app")
```

## Advanced

### Adjusting cache TTL

???+ tip
	`max_age` parameter is also available in high level functions like `get_parameter`, `get_secret`, etc.

By default, we cache parameters retrieved in-memory for 5 seconds.

You can adjust how long we should keep values in cache by using the param `max_age`, when using  `get()` or `get_multiple()` methods across all providers.

```python hl_lines="9" title="Caching parameter(s) value in memory for longer than 5 seconds"
from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

config = Config(region_name="us-west-1")
ssm_provider = parameters.SSMProvider(config=config)

def handler(event, context):
	# Retrieve a single parameter
	value = ssm_provider.get("/my/parameter", max_age=60) # 1 minute

	# Retrieve multiple parameters from a path prefix
	values = ssm_provider.get_multiple("/my/path/prefix", max_age=60)
	for k, v in values.items():
		print(f"{k}: {v}")
```

### Always fetching the latest

If you'd like to always ensure you fetch the latest parameter from the store regardless if already available in cache, use `force_fetch` param.

```python hl_lines="5" title="Forcefully fetching the latest parameter whether TTL has expired or not"
from aws_lambda_powertools.utilities import parameters

def handler(event, context):
	# Retrieve a single parameter
	value = parameters.get_parameter("/my/parameter", force_fetch=True)
```

### Built-in provider class

For greater flexibility such as configuring the underlying SDK client used by built-in providers, you can use their respective Provider Classes directly.

???+ tip
    This can be used to retrieve values from other regions, change the retry behavior, etc.

#### SSMProvider

```python hl_lines="5 9 12" title="Example with SSMProvider for further extensibility"
from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

config = Config(region_name="us-west-1")
ssm_provider = parameters.SSMProvider(config=config) # or boto3_session=boto3.Session()

def handler(event, context):
	# Retrieve a single parameter
	value = ssm_provider.get("/my/parameter")

	# Retrieve multiple parameters from a path prefix
	values = ssm_provider.get_multiple("/my/path/prefix")
	for k, v in values.items():
		print(f"{k}: {v}")
```

The AWS Systems Manager Parameter Store provider supports two additional arguments for the `get()` and `get_multiple()` methods:

| Parameter     | Default | Description                                                                                    |
| ------------- | ------- | ---------------------------------------------------------------------------------------------- |
| **decrypt**   | `False` | Will automatically decrypt the parameter.                                                      |
| **recursive** | `True`  | For `get_multiple()` only, will fetch all parameter values recursively based on a path prefix. |

```python hl_lines="6 8" title="Example with get() and get_multiple()"
from aws_lambda_powertools.utilities import parameters

ssm_provider = parameters.SSMProvider()

def handler(event, context):
	decrypted_value = ssm_provider.get("/my/encrypted/parameter", decrypt=True)

	no_recursive_values = ssm_provider.get_multiple("/my/path/prefix", recursive=False)
```

#### SecretsProvider

```python hl_lines="5 9" title="Example with SecretsProvider for further extensibility"
from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

config = Config(region_name="us-west-1")
secrets_provider = parameters.SecretsProvider(config=config)

def handler(event, context):
	# Retrieve a single secret
	value = secrets_provider.get("my-secret")
```

#### DynamoDBProvider

The DynamoDB Provider does not have any high-level functions, as it needs to know the name of the DynamoDB table containing the parameters.

**DynamoDB table structure for single parameters**

For single parameters, you must use `id` as the [partition key](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey) for that table.

???+ example

	DynamoDB table with `id` partition key and `value` as attribute

 | id           | value    |
 | ------------ | -------- |
 | my-parameter | my-value |

With this table, `dynamodb_provider.get("my-param")` will return `my-value`.

=== "app.py"
	```python hl_lines="3 7"
	from aws_lambda_powertools.utilities import parameters

	dynamodb_provider = parameters.DynamoDBProvider(table_name="my-table")

	def handler(event, context):
		# Retrieve a value from DynamoDB
		value = dynamodb_provider.get("my-parameter")
	```

=== "DynamoDB Local example"
	You can initialize the DynamoDB provider pointing to [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) using `endpoint_url` parameter:

	```python hl_lines="3"
	from aws_lambda_powertools.utilities import parameters

	dynamodb_provider = parameters.DynamoDBProvider(table_name="my-table", endpoint_url="http://localhost:8000")
	```

**DynamoDB table structure for multiple values parameters**

You can retrieve multiple parameters sharing the same `id` by having a sort key named `sk`.

???+ example

	DynamoDB table with `id` primary key, `sk` as sort key` and `value` as attribute

 | id          | sk      | value      |
 | ----------- | ------- | ---------- |
 | my-hash-key | param-a | my-value-a |
 | my-hash-key | param-b | my-value-b |
 | my-hash-key | param-c | my-value-c |

With this table, `dynamodb_provider.get_multiple("my-hash-key")` will return a dictionary response in the shape of `sk:value`.

=== "app.py"
	```python hl_lines="3 8"
	from aws_lambda_powertools.utilities import parameters

	dynamodb_provider = parameters.DynamoDBProvider(table_name="my-table")

	def handler(event, context):
		# Retrieve multiple values by performing a Query on the DynamoDB table
		# This returns a dict with the sort key attribute as dict key.
		parameters = dynamodb_provider.get_multiple("my-hash-key")
		for k, v in parameters.items():
			# k: param-a
			# v: "my-value-a"
			print(f"{k}: {v}")
	```

=== "parameters dict response"

	```json
	{
		"param-a": "my-value-a",
		"param-b": "my-value-b",
		"param-c": "my-value-c"
	}
	```

**Customizing DynamoDBProvider**

DynamoDB provider can be customized at initialization to match your table structure:

| Parameter      | Mandatory | Default | Description                                                                                                |
| -------------- | --------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| **table_name** | **Yes**   | *(N/A)* | Name of the DynamoDB table containing the parameter values.                                                |
| **key_attr**   | No        | `id`    | Hash key for the DynamoDB table.                                                                           |
| **sort_attr**  | No        | `sk`    | Range key for the DynamoDB table. You don't need to set this if you don't use the `get_multiple()` method. |
| **value_attr** | No        | `value` | Name of the attribute containing the parameter value.                                                      |

```python hl_lines="3-8" title="Customizing DynamoDBProvider to suit your table design"
from aws_lambda_powertools.utilities import parameters

dynamodb_provider = parameters.DynamoDBProvider(
	table_name="my-table",
	key_attr="MyKeyAttr",
	sort_attr="MySortAttr",
	value_attr="MyvalueAttr"
)

def handler(event, context):
	value = dynamodb_provider.get("my-parameter")
```

#### AppConfigProvider

```python hl_lines="5 9" title="Using AppConfigProvider"
from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

config = Config(region_name="us-west-1")
appconf_provider = parameters.AppConfigProvider(environment="my_env", application="my_app", config=config)

def handler(event, context):
	# Retrieve a single secret
	value: bytes = appconf_provider.get("my_conf")
```

### Create your own provider

You can create your own custom parameter store provider by inheriting the `BaseProvider` class, and implementing both `_get()` and `_get_multiple()` methods to retrieve a single, or multiple parameters from your custom store.

All transformation and caching logic is handled by the `get()` and `get_multiple()` methods from the base provider class.

Here is an example implementation using S3 as a custom parameter store:

```python hl_lines="3 6 17 27" title="Creating a S3 Provider to fetch parameters"
import copy

from aws_lambda_powertools.utilities import BaseProvider
import boto3

class S3Provider(BaseProvider):
	bucket_name = None
	client = None

	def __init__(self, bucket_name: str):
		# Initialize the client to your custom parameter store
		# E.g.:

		self.bucket_name = bucket_name
		self.client = boto3.client("s3")

	def _get(self, name: str, **sdk_options) -> str:
		# Retrieve a single value
		# E.g.:

		sdk_options["Bucket"] = self.bucket_name
		sdk_options["Key"] = name

		response = self.client.get_object(**sdk_options)
		return

	def _get_multiple(self, path: str, **sdk_options) -> Dict[str, str]:
		# Retrieve multiple values
		# E.g.:

		list_sdk_options = copy.deepcopy(sdk_options)

		list_sdk_options["Bucket"] = self.bucket_name
		list_sdk_options["Prefix"] = path

		list_response = self.client.list_objects_v2(**list_sdk_options)

		parameters = {}

		for obj in list_response.get("Contents", []):
			get_sdk_options = copy.deepcopy(sdk_options)

			get_sdk_options["Bucket"] = self.bucket_name
			get_sdk_options["Key"] = obj["Key"]

			get_response = self.client.get_object(**get_sdk_options)

			parameters[obj["Key"]] = get_response["Body"].read().decode()

		return parameters
```

### Deserializing values with transform parameter

For parameters stored in JSON or Base64 format, you can use the `transform` argument for deserialization.

???+ info
    The `transform` argument is available across all providers, including the high level functions.

=== "High level functions"

    ```python hl_lines="4"
    from aws_lambda_powertools.utilities import parameters

    def handler(event, context):
        value_from_json = parameters.get_parameter("/my/json/parameter", transform="json")
    ```

=== "Providers"

    ```python hl_lines="7 10"
    from aws_lambda_powertools.utilities import parameters

    ssm_provider = parameters.SSMProvider()

    def handler(event, context):
        # Transform a JSON string
        value_from_json = ssm_provider.get("/my/json/parameter", transform="json")

        # Transform a Base64 encoded string
        value_from_binary = ssm_provider.get("/my/binary/parameter", transform="binary")
    ```

#### Partial transform failures with `get_multiple()`

If you use `transform` with `get_multiple()`, you can have a single malformed parameter value. To prevent failing the entire request, the method will return a `None` value for the parameters that failed to transform.

You can override this by setting the `raise_on_transform_error` argument to `True`. If you do so, a single transform error will raise a **`TransformParameterError`** exception.

For example, if you have three parameters, */param/a*, */param/b* and */param/c*, but */param/c* is malformed:

```python hl_lines="9 16" title="Raising TransformParameterError at first malformed parameter"
from aws_lambda_powertools.utilities import parameters

ssm_provider = parameters.SSMProvider()

def handler(event, context):
	# This will display:
	# /param/a: [some value]
	# /param/b: [some value]
	# /param/c: None
	values = ssm_provider.get_multiple("/param", transform="json")
	for k, v in values.items():
		print(f"{k}: {v}")

	try:
		# This will raise a TransformParameterError exception
		values = ssm_provider.get_multiple("/param", transform="json", raise_on_transform_error=True)
	except parameters.exceptions.TransformParameterError:
		...
```

#### Auto-transform values on suffix

If you use `transform` with `get_multiple()`, you might want to retrieve and transform parameters encoded in different formats.

You can do this with a single request by using `transform="auto"`. This will instruct any Parameter to to infer its type based on the suffix and transform it accordingly.

???+ info
    `transform="auto"` feature is available across all providers, including the high level functions.

```python hl_lines="6" title="Deserializing parameter values based on their suffix"
from aws_lambda_powertools.utilities import parameters

ssm_provider = parameters.SSMProvider()

def handler(event, context):
	values = ssm_provider.get_multiple("/param", transform="auto")
```

For example, if you have two parameters with the following suffixes `.json` and `.binary`:

| Parameter name  | Parameter value      |
| --------------- | -------------------- |
| /param/a.json   | [some encoded value] |
| /param/a.binary | [some encoded value] |

The return of `ssm_provider.get_multiple("/param", transform="auto")` call will be a dictionary like:

```json
{
    "a.json": [some value],
    "b.binary": [some value]
}
```

### Passing additional SDK arguments

You can use arbitrary keyword arguments to pass it directly to the underlying SDK method.

```python hl_lines="8" title=""
from aws_lambda_powertools.utilities import parameters

secrets_provider = parameters.SecretsProvider()

def handler(event, context):
	# The 'VersionId' argument will be passed to the underlying get_secret_value() call.
	value = secrets_provider.get("my-secret", VersionId="e62ec170-6b01-48c7-94f3-d7497851a8d2")
```

Here is the mapping between this utility's functions and methods and the underlying SDK:

| Provider            | Function/Method                 | Client name      | Function name                                                                                                                                             |
| ------------------- | ------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SSM Parameter Store | `get_parameter`                 | `ssm`            | [get_parameter](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter)                             |
| SSM Parameter Store | `get_parameters`                | `ssm`            | [get_parameters_by_path](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameters_by_path)           |
| SSM Parameter Store | `SSMProvider.get`               | `ssm`            | [get_parameter](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter)                             |
| SSM Parameter Store | `SSMProvider.get_multiple`      | `ssm`            | [get_parameters_by_path](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameters_by_path)           |
| Secrets Manager     | `get_secret`                    | `secretsmanager` | [get_secret_value](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_secret_value) |
| Secrets Manager     | `SecretsManager.get`            | `secretsmanager` | [get_secret_value](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_secret_value) |
| DynamoDB            | `DynamoDBProvider.get`          | `dynamodb`       | ([Table resource](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table))                                        | [get_item](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.get_item) |
| DynamoDB            | `DynamoDBProvider.get_multiple` | `dynamodb`       | ([Table resource](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table))                                        | [query](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query)       |
| App Config          | `get_app_config`                | `appconfig`      | [get_configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/appconfig.html#AppConfig.Client.get_configuration)         |

### Bring your own boto client

You can use `boto3_client` parameter via any of the available [Provider Classes](#built-in-provider-class). Some providers expect a low level boto3 client while others expect a high level boto3 client, here is the mapping for each of them:

| Provider                                | Type       | Boto client construction     |
| --------------------------------------- | ---------- | ---------------------------- |
| [SSMProvider](#ssmprovider)             | low level  | `boto3.client("ssm")`        |
| [SecretsProvider](#secretsprovider)     | low level  | `boto3.client("secrets")`    |
| [AppConfigProvider](#appconfigprovider) | low level  | `boto3.client("appconfig")`  |
| [DynamoDBProvider](#dynamodbprovider)   | high level | `boto3.resource("dynamodb")` |

Bringing them together in a single code snippet would look like this:

```python title="Example: passing a custom boto3 client for each provider"
import boto3
from botocore.config import Config

from aws_lambda_powertools.utilities import parameters

config = Config(region_name="us-west-1")

# construct boto clients with any custom configuration
ssm = boto3.client("ssm", config=config)
secrets = boto3.client("secrets", config=config)
appconfig = boto3.client("appconfig", config=config)
dynamodb = boto3.resource("dynamodb", config=config)

ssm_provider = parameters.SSMProvider(boto3_client=ssm)
secrets_provider = parameters.SecretsProvider(boto3_client=secrets)
appconf_provider = parameters.AppConfigProvider(boto3_client=appconfig, environment="my_env", application="my_app")
dynamodb_provider = parameters.DynamoDBProvider(boto3_client=dynamodb, table_name="my-table")

```

???+ question "When is this useful?"
	Injecting a custom boto3 client can make unit/snapshot testing easier, including SDK customizations.

### Customizing boto configuration

The **`config`** , **`boto3_session`**, and **`boto3_client`**  parameters enable you to pass in a custom [botocore config object](https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html) , [boto3 session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html), or  a [boto3 client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html) when constructing any of the built-in provider classes.

???+ tip
	You can use a custom session for retrieving parameters cross-account/region and for snapshot testing.

	When using VPC private endpoints, you can pass a custom client altogether. It's also useful for testing when injecting fake instances.

=== "Custom session"

	```python hl_lines="2 4 5"
	from aws_lambda_powertools.utilities import parameters
	import boto3

	boto3_session = boto3.session.Session()
	ssm_provider = parameters.SSMProvider(boto3_session=boto3_session)

	def handler(event, context):
		# Retrieve a single parameter
		value = ssm_provider.get("/my/parameter")
		...
	```
=== "Custom config"

	```python hl_lines="2 4 5"
	from aws_lambda_powertools.utilities import parameters
	from botocore.config import Config

	boto_config = Config()
	ssm_provider = parameters.SSMProvider(config=boto_config)

	def handler(event, context):
		# Retrieve a single parameter
		value = ssm_provider.get("/my/parameter")
		...
	```

=== "Custom client"

	```python hl_lines="2 4 5"
	from aws_lambda_powertools.utilities import parameters
	import boto3

	boto3_client= boto3.client("ssm")
	ssm_provider = parameters.SSMProvider(boto3_client=boto3_client)

	def handler(event, context):
		# Retrieve a single parameter
		value = ssm_provider.get("/my/parameter")
		...
	```

## Testing your code

### Mocking parameter values

For unit testing your applications, you can mock the calls to the parameters utility to avoid calling AWS APIs. This can be achieved in a number of ways - in this example, we use the [pytest monkeypatch fixture](https://docs.pytest.org/en/latest/how-to/monkeypatch.html) to patch the `parameters.get_parameter` method:

=== "tests.py"
	```python
	from src import index

	def test_handler(monkeypatch):

		def mockreturn(name):
			return "mock_value"

		monkeypatch.setattr(index.parameters, "get_parameter", mockreturn)
		return_val = index.handler({}, {})
		assert return_val.get('message') == 'mock_value'
	```

=== "src/index.py"
	```python
	from aws_lambda_powertools.utilities import parameters

	def handler(event, context):
		# Retrieve a single parameter
		value = parameters.get_parameter("my-parameter-name")
		return {"message": value}
	```

If we need to use this pattern across multiple tests, we can avoid repetition by refactoring to use our own pytest fixture:

=== "tests.py"
	```python
	import pytest

	from src import index

	@pytest.fixture
	def mock_parameter_response(monkeypatch):
		def mockreturn(name):
			return "mock_value"

    	monkeypatch.setattr(index.parameters, "get_parameter", mockreturn)

	# Pass our fixture as an argument to all tests where we want to mock the get_parameter response
	def test_handler(mock_parameter_response):
		return_val = index.handler({}, {})
		assert return_val.get('message') == 'mock_value'

	```

Alternatively, if we need more fully featured mocking (for example checking the arguments passed to `get_parameter`), we
can use [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) from the python stdlib instead of pytest's `monkeypatch` fixture. In this example, we use the
[patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch) decorator to replace the `aws_lambda_powertools.utilities.parameters.get_parameter` function with a [MagicMock](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.MagicMock)
object named `get_parameter_mock`.

=== "tests.py"
	```python
	from unittest.mock import patch
	from src import index

	# Replaces "aws_lambda_powertools.utilities.parameters.get_parameter" with a Mock object
	@patch("aws_lambda_powertools.utilities.parameters.get_parameter")
	def test_handler(get_parameter_mock):
		get_parameter_mock.return_value = 'mock_value'

		return_val = index.handler({}, {})
		get_parameter_mock.assert_called_with("my-parameter-name")
		assert return_val.get('message') == 'mock_value'

	```

### Clearing cache

Parameters utility caches all parameter values for performance and cost reasons. However, this can have unintended interference in tests using the same parameter name.

Within your tests, you can use `clear_cache` method available in [every provider](#built-in-provider-class). When using multiple providers or higher level functions like `get_parameter`, use `clear_caches` standalone function to clear cache globally.

=== "clear_cache method"
	```python hl_lines="9"
    import pytest

    from src import app


    @pytest.fixture(scope="function", autouse=True)
	def clear_parameters_cache():
		yield
		app.ssm_provider.clear_cache() # This will clear SSMProvider cache

	@pytest.fixture
    def mock_parameter_response(monkeypatch):
        def mockreturn(name):
            return "mock_value"

        monkeypatch.setattr(app.ssm_provider, "get", mockreturn)

    # Pass our fixture as an argument to all tests where we want to mock the get_parameter response
    def test_handler(mock_parameter_response):
        return_val = app.handler({}, {})
        assert return_val.get('message') == 'mock_value'
	```

=== "global clear_caches"
	```python hl_lines="10"
    import pytest

	from aws_lambda_powertools.utilities import parameters
    from src import app


    @pytest.fixture(scope="function", autouse=True)
	def clear_parameters_cache():
		yield
		parameters.clear_caches() # This will clear all providers cache

	@pytest.fixture
    def mock_parameter_response(monkeypatch):
        def mockreturn(name):
            return "mock_value"

        monkeypatch.setattr(app.ssm_provider, "get", mockreturn)

    # Pass our fixture as an argument to all tests where we want to mock the get_parameter response
    def test_handler(mock_parameter_response):
        return_val = app.handler({}, {})
        assert return_val.get('message') == 'mock_value'
	```

=== "app.py"
	```python
    from aws_lambda_powertools.utilities import parameters
    from botocore.config import Config

    ssm_provider = parameters.SSMProvider(config=Config(region_name="us-west-1"))


    def handler(event, context):
        value = ssm_provider.get("/my/parameter")
		return {"message": value}
	```
