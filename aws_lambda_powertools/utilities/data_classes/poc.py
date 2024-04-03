from typing import Iterator
import json
from aws_lambda_powertools.utilities.data_classes import S3Event, SQSEvent, SNSEvent, SESEvent, EventBridgeEvent
from aws_lambda_powertools.utilities.data_classes.sns_event import SNSMessage
from aws_lambda_powertools.utilities.data_classes.ses_event import SESEventRecord, SESMail, SESMessage
import test_events


def lambda_handler_sqs_s3(event: SQSEvent = test_events.sqs_s3_event): # sqs(s3)
    sqs_event = SQSEvent(event)
    s3_event = sqs_event.decode_nested_events(S3Event)
    for rec in s3_event:
        print('rec:', rec.bucket_name)

def lambda_handler_sqs_sns(event: SQSEvent = test_events.sqs_sns_event): # sqs(sns)
    sqs_event = SQSEvent(event)
    sns_event = sqs_event.decode_nested_events(SNSMessage)
    for rec in sns_event:
        print('rec:', type(rec))
        print(rec.message)
        # try:
        #     validate(instance=rec, schema=test_events.sns_schema)
        #     print("JSON object is valid.")
        # except jsonschema.exceptions.ValidationError:
        #     print("JSON object is not valid.")
        #     # rec = json.dumps(rec)
        #     asdf = SNSEvent({"Records": {"Sns": rec.records}})
        #     print(asdf)


def lambda_handler_sns_s3(event: SNSEvent = test_events.sns_s3_event): # sns(s3)
    sns_event = SNSEvent(event)
    s3_event = sns_event.decode_nested_events(S3Event)
    for rec in s3_event:
        print(type(rec))
        print('rec:', rec.bucket_name)


def lambda_handler_sqs_s3_multi(event: SQSEvent = test_events.sqs_s3_multi_event): # sqs(s3, s3)
    sqs_event = SQSEvent(event)
    s3_event = sqs_event.decode_nested_events(S3Event)
    for rec in s3_event:
        print('rec:', rec.bucket_name)


def lambda_handler_sqs_sns_s3(event: SQSEvent = test_events.sqs_sns_s3_event): # sqs(sns(s3))
    sqs_event = SQSEvent(event)
    sns_event = sqs_event.decode_nested_events(SNSMessage)
    for rec in sns_event:
        print('sns rec:', type(rec), rec)
        print('sns message:', rec.message)

        s3_event = rec.decode_nested_events(S3Event)
        print('s3 rec:', type(s3_event), s3_event)
        # print(s3_event.bucket_name) # not working
        print(next(s3_event).bucket_name) # TODO: why isn't it calling snsmessage nested events without this line?


def lambda_handler_sns_ses(event: SNSEvent = test_events.sns_ses_event): # sns(ses)
    sns_event = SNSEvent(event)
    ses_event = sns_event.decode_nested_events(SESMessage)
    for rec in ses_event:
        print('rec:', type(rec), rec)
        print('rec:', rec.get("mail").get('source'))
        # print('rec:', rec.mail) #but can't do rec.mail bc no "SES" key..

def lambda_handler_eb_s3(event: EventBridgeEvent = test_events.eb_s3_event): # eventbridge(s3)
    eb_event = EventBridgeEvent(event)
    s3_event = eb_event.decode_nested_events(S3Event)
    for rec in s3_event:
        print('type:', type(rec))
        print('rec:', rec.bucket_name)

def lambda_handler_sqs_eb_s3(event: test_events.sqs_eb_s3_event): # sqs(eventbridge(s3))
    sqs_event = SQSEvent(event)
    for rec in sqs_event:
        eb_event = sqs_event.decode_nested_events(EventBridgeEvent)
        for rec in eb_event:
            print('rec:', type(rec), rec)
            s3_event = rec.decode_nested_events(S3Event)
            for r in s3_event:
                print(type(r))
                print('rec:', r.bucket_name)


lambda_handler_sqs_s3(test_events.sqs_s3_event)
lambda_handler_sqs_sns(test_events.sqs_sns_event)
lambda_handler_sns_s3(test_events.sns_s3_event)
lambda_handler_sqs_s3_multi(test_events.sqs_s3_multi_event)
lambda_handler_sqs_sns_s3(test_events.sqs_sns_s3_event)
lambda_handler_sns_ses(test_events.sns_ses_event) # not being casted correctly bc no "SES" key but works as dict
# lambda_handler_eb_s3(test_events.eb_s3_event) #the nested s3 event isn't a full s3 event bc doesn't have a Records key at the top level. so can't call the s3 methods on it
# lambda_handler_sqs_eb_s3(test_events.sqs_eb_s3_event) #same as above
