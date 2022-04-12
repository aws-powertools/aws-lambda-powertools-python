---
title: Validation
description: Utility
---

This utility provides JSON Schema validation for events and responses, including JMESPath support to unwrap events before validation.

## Key features

* Validate incoming event and response
* JMESPath support to unwrap events before validation applies
* Built-in envelopes to unwrap popular event sources payloads

## Getting started

???+ tip "Tip: Using JSON Schemas for the first time?"
    Check this [step-by-step tour in the official JSON Schema website](https://json-schema.org/learn/getting-started-step-by-step.html){target="_blank"}.

You can validate inbound and outbound events using [`validator` decorator](#validator-decorator).

You can also use the standalone `validate` function, if you want more control over the validation process such as handling a validation error.

We support any JSONSchema draft supported by [fastjsonschema](https://horejsek.github.io/python-fastjsonschema/){target="_blank"} library.

???+ warning
    Both `validator` decorator and `validate` standalone function expects your JSON Schema to be a **dictionary**, not a filename.

### Validator decorator

**Validator** decorator is typically used to validate either inbound or functions' response.

It will fail fast with `SchemaValidationError` exception if event or response doesn't conform with given JSON Schema.

=== "validator_decorator.py"

    ```python hl_lines="1 6"
    --8<-- "docs/examples/utilities/validation/validator_decorator.py"
    ```

=== "event.json"

    ```json
    {
        "message": "hello world",
        "username": "lessa"
    }
    ```

=== "schemas.py"

    ```python hl_lines="8 10 17 23 34 36 41"
    --8<-- "docs/shared/validation_basic_jsonschema.py"
    ```

???+ note
    It's not a requirement to validate both inbound and outbound schemas - You can either use one, or both.

### Validate function

**Validate** standalone function is typically used within the Lambda handler, or any other methods that perform data validation.

You can also gracefully handle schema validation errors by catching `SchemaValidationError` exception.

=== "validator_function.py"

    ```python hl_lines="9"
    --8<-- "docs/examples/utilities/validation/validator_function.py"
    ```

=== "event.json"

    ```json
    {
        "data": "hello world",
        "username": "lessa"
    }
    ```

=== "schemas.py"

    ```python hl_lines="8 10 17 23 34 36 41"
    --8<-- "docs/shared/validation_basic_jsonschema.py"
    ```

### Unwrapping events prior to validation

You might want to validate only a portion of your event - This is where the `envelope` parameter is for.

Envelopes are [JMESPath expressions](https://jmespath.org/tutorial.html) to extract a portion of JSON you want before applying JSON Schema validation.

Here is a sample custom EventBridge event, where we only validate what's inside the `detail` key:

=== "unwrapping_events.py"

    We use the `envelope` parameter to extract the payload inside the `detail` key before validating.

    ```python hl_lines="6"
    --8<-- "docs/examples/utilities/validation/unwrapping_events.py"
    ```

=== "sample_wrapped_event.json"

    ```python hl_lines="11-14"
    --8<-- "docs/shared/validation_basic_eventbridge_event.json"
    ```

=== "schemas.py"

    ```python hl_lines="8 10 17 23 34 36 41"
    --8<-- "docs/shared/validation_basic_jsonschema.py"
    ```

This is quite powerful because you can use JMESPath Query language to extract records from [arrays, slice and dice](https://jmespath.org/tutorial.html#list-and-slice-projections), to [pipe expressions](https://jmespath.org/tutorial.html#pipe-expressions) and [function expressions](https://jmespath.org/tutorial.html#functions), where you'd extract what you need before validating the actual payload.

### Built-in envelopes

This utility comes with built-in envelopes to easily extract the payload from popular event sources.

=== "unwrapping_popular_event_sources.py"

    ```python hl_lines="6 8"
    --8<-- "docs/examples/utilities/validation/unwrapping_popular_event_sources.py"
    ```

=== "sample_wrapped_event.json"

    ```python hl_lines="11-14"
    --8<-- "docs/shared/validation_basic_eventbridge_event.json"
    ```

=== "schemas.py"

    ```python hl_lines="8 10 17 23 34 36 41"
    --8<-- "docs/shared/validation_basic_jsonschema.py"
    ```

Here is a handy table with built-in envelopes along with their JMESPath expressions in case you want to build your own.

Envelope name | JMESPath expression
------------------------------------------------- | ---------------------------------------------------------------------------------
**API_GATEWAY_REST** | "powertools_json(body)"
**API_GATEWAY_HTTP** | "powertools_json(body)"
**SQS** | "Records[*].powertools_json(body)"
**SNS** | "Records[0].Sns.Message | powertools_json(@)"
**EVENTBRIDGE** | "detail"
**CLOUDWATCH_EVENTS_SCHEDULED** | "detail"
**KINESIS_DATA_STREAM** | "Records[*].kinesis.powertools_json(powertools_base64(data))"
**CLOUDWATCH_LOGS** | "awslogs.powertools_base64_gzip(data) | powertools_json(@).logEvents[*]"

## Advanced

### Validating custom formats

???+ note
    JSON Schema DRAFT 7 [has many new built-in formats](https://json-schema.org/understanding-json-schema/reference/string.html#format){target="_blank"} such as date, time, and specifically a regex format which might be a better replacement for a custom format, if you do have control over the schema.

JSON Schemas with custom formats like `int64` will fail validation. If you have these, you can pass them using `formats` parameter:

```json title="custom_json_schema_type_format.json"
{
	"lastModifiedTime": {
		"format": "int64",
		"type": "integer"
	}
}
```

For each format defined in a dictionary key, you must use a regex, or a function that returns a boolean to instruct the validator on how to proceed when encountering that type.

=== "validate_custom_format.py"

    ```python hl_lines="5-8 10"
    --8<-- "docs/examples/utilities/validation/validate_custom_format.py"
    ```

=== "schemas.py"

    ```python hl_lines="68 91  93"
    --8<-- "docs/examples/utilities/validation/validate_jsonschema.py"
    ```

=== "event.json"

    ```json
    {
        "account": "123456789012",
        "detail": {
            "additionalEventData": {
                "AuthenticationMethod": "AuthHeader",
                "CipherSuite": "ECDHE-RSA-AES128-GCM-SHA256",
                "SignatureVersion": "SigV4",
                "bytesTransferredIn": 0,
                "bytesTransferredOut": 0,
                "x-amz-id-2": "ejUr9Nd/4IO1juF/a6GOcu+PKrVX6dOH6jDjQOeCJvtARUqzxrhHGrhEt04cqYtAZVqcSEXYqo0=",
            },
            "awsRegion": "us-west-1",
            "eventCategory": "Data",
            "eventID": "be4fdb30-9508-4984-b071-7692221899ae",
            "eventName": "HeadObject",
            "eventSource": "s3.amazonaws.com",
            "eventTime": "2020-12-22T10:05:29Z",
            "eventType": "AwsApiCall",
            "eventVersion": "1.07",
            "managementEvent": False,
            "readOnly": True,
            "recipientAccountId": "123456789012",
            "requestID": "A123B1C123D1E123",
            "requestParameters": {
                "Host": "lambda-artifacts-deafc19498e3f2df.s3.us-west-1.amazonaws.com",
                "bucketName": "lambda-artifacts-deafc19498e3f2df",
                "key": "path1/path2/path3/file.zip",
            },
            "resources": [
                {
                    "ARN": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df/path1/path2/path3/file.zip",
                    "type": "AWS::S3::Object",
                },
                {
                    "ARN": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df",
                    "accountId": "123456789012",
                    "type": "AWS::S3::Bucket",
                },
            ],
            "responseElements": None,
            "sourceIPAddress": "AWS Internal",
            "userAgent": "AWS Internal",
            "userIdentity": {
                "accessKeyId": "ABCDEFGHIJKLMNOPQR12",
                "accountId": "123456789012",
                "arn": "arn:aws:sts::123456789012:assumed-role/role-name1/1234567890123",
                "invokedBy": "AWS Internal",
                "principalId": "ABCDEFGHIJKLMN1OPQRST:1234567890123",
                "sessionContext": {
                    "attributes": {"creationDate": "2020-12-09T09:58:24Z", "mfaAuthenticated": "false"},
                    "sessionIssuer": {
                        "accountId": "123456789012",
                        "arn": "arn:aws:iam::123456789012:role/role-name1",
                        "principalId": "ABCDEFGHIJKLMN1OPQRST",
                        "type": "Role",
                        "userName": "role-name1",
                    },
                },
                "type": "AssumedRole",
            },
            "vpcEndpointId": "vpce-a123cdef",
        },
        "detail-type": "AWS API Call via CloudTrail",
        "id": "e0bad426-0a70-4424-b53a-eb902ebf5786",
        "region": "us-west-1",
        "resources": [],
        "source": "aws.s3",
        "time": "2020-12-22T10:05:29Z",
        "version": "0",
    }
    ```

### Built-in JMESPath functions

You might have events or responses that contain non-encoded JSON, where you need to decode before validating them.

You can use our built-in [JMESPath functions](/utilities/jmespath_functions) within your expressions to do exactly that to decode JSON Strings, base64, and uncompress gzip data.

???+ info
    We use these for built-in envelopes to easily to decode and unwrap events from sources like Kinesis, CloudWatch Logs, etc.
