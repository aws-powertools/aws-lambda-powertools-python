"""
Amazon DynamoDB parameter retrieval and caching utility
"""


from typing import Dict, Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config

from .base import BaseProvider


class DynamoDBProvider(BaseProvider):
    """
    Amazon DynamoDB Parameter Provider

    Parameters
    ----------
    table_name: str
        Name of the DynamoDB table that stores parameters
    key_attr: str, optional
        Hash key for the DynamoDB table
    value_attr: str, optional
        Attribute that contains the values in the DynamoDB table
    config: botocore.config.Config, optional
        Botocore configuration to pass during client initialization

    Example
    -------
    **Retrieves a parameter value from a DynamoDB table**

    In this example, the DynamoDB table uses `id` as hash key and stores the value in the `value`
    attribute. The parameter item looks like this:

        { "id": "my-parameters", "value": "Parameter value a" }

        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>> ddb_provider = DynamoDBProvider("ParametersTable")
        >>>
        >>> value = ddb_provider.get("my-parameter")
        >>>
        >>> print(value)
        My parameter value

    **Retrieves a parameter value from a DynamoDB table that has custom attribute names**

        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>> ddb_provider = DynamoDBProvider(
        ...     "ParametersTable",
        ...     key_attr="my-id",
        ...     value_attr="my-value"
        ... )
        >>>
        >>> value = ddb_provider.get("my-parameter")
        >>>
        >>> print(value)
        My parameter value

    **Retrieves a parameter value from a DynamoDB table in another AWS region**

        >>> from botocore.config import Config
        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>>
        >>> config = Config(region_name="us-west-1")
        >>> ddb_provider = DynamoDBProvider("ParametersTable", config=config)
        >>>
        >>> value = ddb_provider.get("my-parameter")
        >>>
        >>> print(value)
        My parameter value

    **Retrieves a parameter value from a DynamoDB table passing options to the SDK call**

        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>> ddb_provider = DynamoDBProvider("ParametersTable")
        >>>
        >>> value = ddb_provider.get("my-parameter", ConsistentRead=True)
        >>>
        >>> print(value)
        My parameter value

    **Retrieves multiple values from a DynamoDB table**

    In this case, the provider will use a sort key to retrieve multiple values using a query under
    the hood. This expects that the sort key is named `sk`. The DynamoDB table contains three items
    looking like this:

        { "id": "my-parameters", "sk": "a", "value": "Parameter value a" }
        { "id": "my-parameters", "sk": "b", "value": "Parameter value b" }
        { "id": "my-parameters", "sk": "c", "value": "Parameter value c" }

        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>> ddb_provider = DynamoDBProvider("ParametersTable")
        >>>
        >>> values = ddb_provider.get_multiple("my-parameters")
        >>>
        >>> for key, value in values.items():
        ...     print(key, value)
        a   Parameter value a
        b   Parameter value b
        c   Parameter value c

    **Retrieves multiple values from a DynamoDB table with a custom sort key**

    In this case, the provider will use a sort key to retrieve multiple values using a query under
    the hood.

        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>> ddb_provider = DynamoDBProvider("ParametersTable")
        >>>
        >>> values = ddb_provider.get_multiple("my-parameters", sort_attr="my-sort-attr")
        >>>
        >>> for key, value in values.items():
        ...     print(key, value)
        a   Parameter value a
        b   Parameter value b
        c   Parameter value c

    **Retrieves multiple values from a DynamoDB table passing options to the SDK calls**

        >>> from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
        >>> ddb_provider = DynamoDBProvider("ParametersTable")
        >>>
        >>> values = ddb_provider.get_multiple("my-parameters", ConsistentRead=True)
        >>>
        >>> for key, value in values.items():
        ...     print(key, value)
        a   Parameter value a
        b   Parameter value b
        c   Parameter value c
    """

    table = None
    key_attr = None
    value_attr = None

    def __init__(
        self, table_name: str, key_attr: str = "id", value_attr: str = "value", config: Optional[Config] = None,
    ):
        """
        Initialize the DynamoDB client
        """

        config = config or Config()
        self.table = boto3.resource("dynamodb", config=config).Table(table_name)

        self.key_attr = key_attr
        self.value_attr = value_attr

        super().__init__()

    def _get(self, name: str, **sdk_options) -> str:
        """
        Retrieve a parameter value from Amazon DynamoDB

        Parameters
        ----------
        name: str
            Name of the parameter
        sdk_options: dict, optional
            Dictionary of options that will be passed to the DynamoDB get_item API call
        """

        # Explicit arguments will take precedence over keyword arguments
        sdk_options["Key"] = {self.key_attr: name}

        return self.table.get_item(**sdk_options)["Item"][self.value_attr]

    def _get_multiple(self, path: str, sort_attr: str = "sk", **sdk_options) -> Dict[str, str]:
        """
        Retrieve multiple parameter values from Amazon DynamoDB

        Parameters
        ----------
        path: str
            Path to retrieve the parameters
        sort_attr: str, optional
            Name of the DynamoDB table sort key (defaults to 'sk')
        sdk_options: dict, optional
            Dictionary of options that will be passed to the DynamoDB query API call
        """

        # Explicit arguments will take precedence over keyword arguments
        sdk_options["KeyConditionExpression"] = Key(self.key_attr).eq(path)

        response = self.table.query(**sdk_options)
        items = response.get("Items", [])

        # Keep querying while there are more items matching the partition key
        while "LastEvaluatedKey" in response:
            sdk_options["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = self.table.query(**sdk_options)
            items.extend(response.get("Items", []))

        retval = {}
        for item in items:
            retval[item[sort_attr]] = item[self.value_attr]

        return retval
