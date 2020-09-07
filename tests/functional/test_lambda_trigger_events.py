import json
import os

from aws_lambda_powertools.utilities.trigger import CloudWatchLogsEvent, S3Event, SESEvent, SNSEvent, SQSEvent
from aws_lambda_powertools.utilities.trigger.dynamo_db_stream_event import (
    AttributeValue,
    DynamoDBRecordEventName,
    DynamoDBStreamEvent,
    StreamViewType,
)


def load_event(file_name: str) -> dict:
    full_file_name = os.path.dirname(os.path.realpath(__file__)) + "/../events/" + file_name
    with open(full_file_name) as fp:
        return json.load(fp)


def test_cloud_watch_trigger_event():
    event = CloudWatchLogsEvent(load_event("cloudWatchLogEvent.json"))

    decoded_data = event.cloud_watch_logs_decoded_data()
    log_events = decoded_data.log_events
    log_event = log_events[0]

    assert decoded_data.owner == "123456789123"
    assert decoded_data.log_group == "testLogGroup"
    assert decoded_data.log_stream == "testLogStream"
    assert decoded_data.subscription_filters == ["testFilter"]
    assert decoded_data.message_type == "DATA_MESSAGE"

    assert log_event.log_event_id == "eventId1"
    assert log_event.timestamp == 1440442987000
    assert log_event.message == "[ERROR] First test message"
    assert log_event.extracted_fields is None


def test_dynamo_db_stream_trigger_event():
    event = DynamoDBStreamEvent(load_event("dynamoStreamEvent.json"))

    records = list(event.records)
    record = records[0]
    assert record.aws_region == "us-west-2"
    dynamodb = record.dynamodb
    assert dynamodb is not None
    assert dynamodb.approximate_creation_date_time is None
    keys = dynamodb.keys
    assert keys is not None
    id_key = keys["Id"]
    assert id_key.b_value is None
    assert id_key.bs_value is None
    assert id_key.bool_value is None
    assert id_key.list_value is None
    assert id_key.map_value is None
    assert id_key.n_value == "101"
    assert id_key.ns_value is None
    assert id_key.null_value is None
    assert id_key.s_value is None
    assert id_key.ss_value is None
    message_key = dynamodb.new_image["Message"]
    assert message_key is not None
    assert message_key.s_value == "New item!"
    assert dynamodb.old_image is None
    assert dynamodb.sequence_number == "111"
    assert dynamodb.size_bytes == 26
    assert dynamodb.stream_view_type == StreamViewType.NEW_AND_OLD_IMAGES
    assert record.event_id == "1"
    assert record.event_name is DynamoDBRecordEventName.INSERT
    assert record.event_source == "aws:dynamodb"
    assert record.event_source_arn == "eventsource_arn"
    assert record.event_version == "1.0"
    assert record.user_identity is None


def test_dynamo_attribute_value_list_value():
    example_attribute_value = {"L": [{"S": "Cookies"}, {"S": "Coffee"}, {"N": "3.14159"}]}
    attribute_value = AttributeValue(example_attribute_value)
    list_value = attribute_value.list_value
    assert list_value is not None
    item = list_value[0]
    assert item.s_value == "Cookies"


def test_dynamo_attribute_value_map_value():
    example_attribute_value = {"M": {"Name": {"S": "Joe"}, "Age": {"N": "35"}}}
    attribute_value = AttributeValue(example_attribute_value)
    map_value = attribute_value.map_value
    assert map_value is not None
    item = map_value["Name"]
    assert item.s_value == "Joe"


def test_s3_trigger_event():
    event = S3Event(load_event("s3Event.json"))
    records = list(event.records)
    assert len(records) == 1
    record = records[0]
    assert record.event_version == "2.1"
    assert record.event_source == "aws:s3"
    assert record.aws_region == "us-east-2"
    assert record.event_time == "2019-09-03T19:37:27.192Z"
    assert record.event_name == "ObjectCreated:Put"
    user_identity = record.user_identity
    assert user_identity.principal_id == "AWS:AIDAINPONIXQXHT3IKHL2"
    request_parameters = record.request_parameters
    assert request_parameters.source_ip_address == "205.255.255.255"
    assert record.response_elements["x-amz-request-id"] == "D82B88E5F771F645"
    s3 = record.s3
    assert s3.s3_schema_version == "1.0"
    assert s3.configuration_id == "828aa6fc-f7b5-4305-8584-487c791949c1"
    bucket = s3.bucket
    assert bucket.name == "lambda-artifacts-deafc19498e3f2df"
    assert bucket.owner_identity.principal_id == "A3I5XTEXAMAI3E"
    assert bucket.arn == "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
    assert s3.s3_object.key == "b21b84d653bb07b05b1e6b33684dc11b"
    assert s3.s3_object.size == 1305107
    assert s3.s3_object.etag == "b21b84d653bb07b05b1e6b33684dc11b"
    assert s3.s3_object.version_id is None
    assert s3.s3_object.sequencer == "0C0F6F405D6ED209E1"
    assert record.glacier_event_data is None


def test_s3_glacier_event():
    example_event = {
        "Records": [
            {
                "glacierEventData": {
                    "restoreEventData": {
                        "lifecycleRestorationExpiryTime": "1970-01-01T00:01:00.000Z",
                        "lifecycleRestoreStorageClass": "standard",
                    }
                }
            }
        ]
    }
    event = S3Event(example_event)
    record = next(event.records)
    glacier_event_data = record.glacier_event_data
    assert glacier_event_data is not None
    assert glacier_event_data.restore_event_data.lifecycle_restoration_expiry_time == "1970-01-01T00:01:00.000Z"
    assert glacier_event_data.restore_event_data.lifecycle_restore_storage_class == "standard"


def test_ses_trigger_event():
    event = SESEvent(load_event("sesEvent.json"))

    expected_address = "johndoe@example.com"
    records = list(event.records)
    record = records[0]
    assert record.event_source == "aws:ses"
    assert record.event_version == "1.0"
    mail = record.ses.mail
    assert mail.timestamp == "1970-01-01T00:00:00.000Z"
    assert mail.source == "janedoe@example.com"
    assert mail.message_id == "o3vrnil0e2ic28tr"
    assert mail.destination == [expected_address]
    assert mail.headers_truncated is False
    headers = list(mail.headers)
    assert len(headers) == 10
    assert headers[0].name == "Return-Path"
    assert headers[0].value == "<janedoe@example.com>"
    common_headers = mail.common_headers
    assert common_headers.return_path == "janedoe@example.com"
    assert common_headers.from_header == common_headers["from"]
    assert common_headers.date == "Wed, 7 Oct 2015 12:34:56 -0700"
    assert common_headers.to == [expected_address]
    assert common_headers.message_id == "<0123456789example.com>"
    assert common_headers.subject == "Test Subject"
    receipt = record.ses.receipt
    assert receipt.timestamp == "1970-01-01T00:00:00.000Z"
    assert receipt.processing_time_millis == 574
    assert receipt.recipients == [expected_address]
    assert receipt.spam_verdict.status == "PASS"
    assert receipt.virus_verdict.status == "PASS"
    assert receipt.spf_verdict.status == "PASS"
    assert receipt.dmarc_verdict.status == "PASS"
    action = receipt.action
    assert action.action_type == action["type"]
    assert action.function_arn == action["functionArn"]
    assert action.invocation_type == action["invocationType"]


def test_sns_trigger_event():
    event = SNSEvent(load_event("snsEvent.json"))
    records = list(event.records)
    assert len(records) == 1
    record = records[0]
    assert record.event_version == "1.0"
    assert record.event_subscription_arn == "arn:aws:sns:us-east-2:123456789012:sns-la ..."
    assert record.event_source == "aws:sns"
    sns = record.sns
    assert sns.signature_version == "1"
    assert sns.timestamp == "2019-01-02T12:45:07.000Z"
    assert sns.signature == "tcc6faL2yUC6dgZdmrwh1Y4cGa/ebXEkAi6RibDsvpi+tE/1+82j...65r=="
    assert sns.signing_cert_url == "https://sns.us-east-2.amazonaws.com/SimpleNotificat ..."
    assert sns.message_id == "95df01b4-ee98-5cb9-9903-4c221d41eb5e"
    assert sns.message == "Hello from SNS!"
    message_attributes = sns.message_attributes
    test_message_attribute = message_attributes["Test"]
    assert test_message_attribute.attribute_type == "String"
    assert test_message_attribute.value == "TestString"
    assert sns.message_type == "Notification"
    assert sns.unsubscribe_url == "https://sns.us-east-2.amazonaws.com/?Action=Unsubscri ..."
    assert sns.topic_arn == "arn:aws:sns:us-east-2:123456789012:sns-lambda"
    assert sns.subject == "TestInvoke"


def test_seq_trigger_event():
    event = SQSEvent(load_event("sqsEvent.json"))

    records = list(event.records)
    record = records[0]
    attributes = record.attributes
    message_attributes = record.message_attributes
    test_attr = message_attributes["testAttr"]

    assert len(records) == 2
    assert record.message_id == "059f36b4-87a3-44ab-83d2-661975830a7d"
    assert record.receipt_handle == "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a..."
    assert record.body == "Test message."
    assert attributes.aws_trace_header is None
    assert attributes.approximate_receive_count == "1"
    assert attributes.sent_timestamp == "1545082649183"
    assert attributes.sender_id == "AIDAIENQZJOLO23YVJ4VO"
    assert attributes.approximate_first_receive_timestamp == "1545082649185"
    assert attributes.sequence_number is None
    assert attributes.message_group_id is None
    assert attributes.message_deduplication_id is None
    assert message_attributes["NotFound"] is None
    assert message_attributes.get("NotFound") is None
    assert test_attr.string_value == "100"
    assert test_attr.binary_value == "base64Str"
    assert test_attr.data_type == "Number"
    assert record.md5_of_body == "e4e68fb7bd0e697a0ae8f1bb342846b3"
    assert record.event_source == "aws:sqs"
    assert record.event_source_arn == "arn:aws:sqs:us-east-2:123456789012:my-queue"
    assert record.aws_region == "us-east-2"
