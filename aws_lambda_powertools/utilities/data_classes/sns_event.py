from typing import Dict, Iterator
import test_events
import jsonschema
from jsonschema import validate

from aws_lambda_powertools.utilities.data_classes.common import DictWrapper, EventWrapper


class SNSMessageAttribute(DictWrapper):
    @property
    def get_type(self) -> str:
        """The supported message attribute data types are String, String.Array, Number, and Binary."""
        # Note: this name conflicts with existing python builtins
        return self["Type"]

    @property
    def value(self) -> str:
        """The user-specified message attribute value."""
        return self["Value"]


class SNSMessage(EventWrapper):
    @property
    def signature_version(self) -> str:
        """Version of the Amazon SNS signature used."""
        return self["SignatureVersion"]

    @property
    def timestamp(self) -> str:
        """The time (GMT) when the subscription confirmation was sent."""
        return self["Timestamp"]

    @property
    def signature(self) -> str:
        """Base64-encoded "SHA1withRSA" signature of the Message, MessageId, Type, Timestamp, and TopicArn values."""
        return self["Signature"]

    @property
    def signing_cert_url(self) -> str:
        """The URL to the certificate that was used to sign the message."""
        return self["SigningCertUrl"]

    @property
    def message_id(self) -> str:
        """A Universally Unique Identifier, unique for each message published.

        For a message that Amazon SNS resends during a retry, the message ID of the original message is used."""
        return self["MessageId"]

    @property
    def message(self) -> str:
        """A string that describes the message."""
        return self["Message"]

    @property
    def message_attributes(self) -> Dict[str, SNSMessageAttribute]:
        return {k: SNSMessageAttribute(v) for (k, v) in self["MessageAttributes"].items()}

    @property
    def get_type(self) -> str:
        """The type of message.

        For a subscription confirmation, the type is SubscriptionConfirmation."""
        # Note: this name conflicts with existing python builtins
        return self["Type"]

    @property
    def unsubscribe_url(self) -> str:
        """A URL that you can use to unsubscribe the endpoint from this topic.

        If you visit this URL, Amazon SNS unsubscribes the endpoint and stops sending notifications to this endpoint."""
        return self["UnsubscribeUrl"]

    @property
    def topic_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the topic that this endpoint is subscribed to."""
        return self["TopicArn"]

    @property
    def subject(self) -> str:
        """The Subject parameter specified when the notification was published to the topic."""
        return self["Subject"]

    def nested_event_contents(self):
        print('in SNS MESSAGE NESTED EVENT')
        yield self.message
        # for record in self.message:
        #     print('record:', record, type(record))
        #     # body = record['Sns']['Message']
        #     # print('body:', body, type(body))
        #     yield record


class SNSEventRecord(EventWrapper):
    @property
    def event_version(self) -> str:
        """Event version"""
        return self["EventVersion"]

    @property
    def event_subscription_arn(self) -> str:
        return self["EventSubscriptionArn"]

    @property
    def event_source(self) -> str:
        """The AWS service from which the SNS event record originated. For SNS, this is aws:sns"""
        return self["EventSource"]

    @property
    def sns(self) -> SNSMessage:
        return SNSMessage(self._data["Sns"])


class SNSEvent(EventWrapper):
    """SNS Event

    Documentation:
    -------------
    - https://docs.aws.amazon.com/lambda/latest/dg/with-sns.html
    """

    @property
    def records(self) -> Iterator[SNSEventRecord]:
        for record in self["Records"]:
            yield SNSEventRecord(record)

    @property
    def record(self) -> SNSEventRecord:
        """Return the first SNS event record"""
        return next(self.records)

    @property
    def sns_message(self) -> str:
        """Return the message for the first sns event record"""
        return self.record.sns.message

    def nested_event_contents(self):
        print('in SNS NESTED EVENT')
        for record in self["Records"]:
            body = record['Sns']['Message']
            yield body

    def check_schema(self):
        print(self, type(self))
        try:
            validate(instance=self, schema=test_events.sns_schema)
            print("JSON object is valid.")
            return self
        except jsonschema.exceptions.ValidationError: #TODO: or cx needs to tell us to cast to SNSEvent or SNSMessage, we shouldn't have to figure that out ourselves?
            print("JSON object is not valid.")
            print("event rec:", SNSMessage(self))
            corrected = SNSMessage(self)
            return corrected
