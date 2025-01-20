import pytest

from aws_lambda_powertools.event_handler.async_execution.routes.event_bridge import (
    EventBridgeRoute,
)
from aws_lambda_powertools.utilities.data_classes.event_bridge_event import (
    EventBridgeEvent,
)
from tests.functional.utils import load_event


class TestEventBridgeRoute:
    def test_constructor_error(self):
        with pytest.raises(ValueError):
            EventBridgeRoute(func=lambda *_: None)

    @pytest.mark.parametrize(
        "option_constructor, expected",
        [
            (
                {"func": None, "resources": "test"},
                {"func": None, "detail_type": None, "source": None, "resources": ["test"]},
            ),
            (
                {"func": None, "resources": ["test"]},
                {"func": None, "detail_type": None, "source": None, "resources": ["test"]},
            ),
            (
                {"func": None, "resources": ["test", "name"]},
                {"func": None, "detail_type": None, "source": None, "resources": ["test", "name"]},
            ),
        ],
    )
    def test_constructor_normal(self, option_constructor, expected):
        route = EventBridgeRoute(**option_constructor)
        assert route.__dict__ == expected

    @pytest.mark.parametrize(
        "option_constructor, option, expected",
        [
            ({"func": None, "detail_type": "test type"}, {"detail_type": None}, False),
            ({"func": None, "detail_type": "test type"}, {"detail_type": "test type 2"}, False),
            ({"func": None, "detail_type": "test type"}, {"detail_type": "test type"}, True),
        ],
    )
    def test_is_target_with_detail_type(self, option_constructor, option, expected):
        route = EventBridgeRoute(**option_constructor)
        actual = route.is_target_with_detail_type(**option)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option, expected",
        [
            ({"func": None, "source": "aws.ec2"}, {"source": None}, False),
            ({"func": None, "source": "aws.ec2"}, {"source": "aws.lambda"}, False),
            ({"func": None, "source": "aws.ec2"}, {"source": "aws.ec2"}, True),
        ],
    )
    def test_is_target_with_source(self, option_constructor, option, expected):
        route = EventBridgeRoute(**option_constructor)
        actual = route.is_target_with_source(**option)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option, expected",
        [
            (
                {"func": None, "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"]},
                {"resources": None},
                False,
            ),
            (
                {"func": None, "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"]},
                {"resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"]},
                False,
            ),
            (
                {"func": None, "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"]},
                {"resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"]},
                True,
            ),
            (
                {
                    "func": None,
                    "resources": [
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0",
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-2222222222abcdef2",
                    ],
                },
                {"resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"]},
                True,
            ),
            (
                {
                    "func": None,
                    "resources": [
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0",
                    ],
                },
                {
                    "resources": [
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-2222222222abcdef2",
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0",
                    ],
                },
                True,
            ),
            (
                {
                    "func": None,
                    "resources": [
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0",
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-3333333333abcdef3",
                    ],
                },
                {
                    "resources": [
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-2222222222abcdef2",
                        "arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0",
                    ],
                },
                True,
            ),
        ],
    )
    def test_is_target_with_resources(self, option_constructor, option, expected):
        route = EventBridgeRoute(**option_constructor)
        actual = route.is_target_with_resources(**option)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "source": "aws.ec2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "source": "aws.ec2",
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "source": "aws.ec2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "detail_type": "EC2 Instance State-change Notification",
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "source": "aws.ec2",
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": lambda *_: None,
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
        ],
    )
    def test_match_true(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = EventBridgeRoute(**option_constructor)
        expected = (route.func, EventBridgeEvent(event))
        actual = route.match(event=event)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            ("activeMQEvent.json", {"func": None, "detail_type": "test"}),
            ("albEvent.json", {"func": None, "detail_type": "test"}),
            ("albEventPathTrailingSlash.json", {"func": None, "detail_type": "test"}),
            ("albMultiValueHeadersEvent.json", {"func": None, "detail_type": "test"}),
            ("albMultiValueQueryStringEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayAuthorizerRequestEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayAuthorizerTokenEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayAuthorizerV2Event.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyEventAnotherPath.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyEventNoOrigin.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyEventPathTrailingSlash.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyEventPrincipalId.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyEvent_noVersionAuth.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyOtherEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2Event.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2EventPathTrailingSlash.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2Event_GET.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2IamEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2LambdaAuthorizerEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2OtherGetEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2SchemaMiddlwareInvalidEvent.json", {"func": None, "detail_type": "test"}),
            ("apiGatewayProxyV2SchemaMiddlwareValidEvent.json", {"func": None, "detail_type": "test"}),
            ("apigatewayeSchemaMiddlwareInvalidEvent.json", {"func": None, "detail_type": "test"}),
            ("apigatewayeSchemaMiddlwareValidEvent.json", {"func": None, "detail_type": "test"}),
            ("appSyncAuthorizerEvent.json", {"func": None, "detail_type": "test"}),
            ("appSyncAuthorizerResponse.json", {"func": None, "detail_type": "test"}),
            ("appSyncBatchEvent.json", {"func": None, "detail_type": "test"}),
            ("appSyncDirectResolver.json", {"func": None, "detail_type": "test"}),
            ("appSyncResolverEvent.json", {"func": None, "detail_type": "test"}),
            ("awsConfigRuleConfigurationChanged.json", {"func": None, "detail_type": "test"}),
            ("awsConfigRuleOversizedConfiguration.json", {"func": None, "detail_type": "test"}),
            ("awsConfigRuleScheduled.json", {"func": None, "detail_type": "test"}),
            ("bedrockAgentEvent.json", {"func": None, "detail_type": "test"}),
            ("bedrockAgentEventWithPathParams.json", {"func": None, "detail_type": "test"}),
            ("bedrockAgentPostEvent.json", {"func": None, "detail_type": "test"}),
            ("cloudWatchAlarmEventCompositeMetric.json", {"func": None, "detail_type": "test"}),
            ("cloudWatchAlarmEventSingleMetric.json", {"func": None, "detail_type": "test"}),
            ("cloudWatchDashboardEvent.json", {"func": None, "detail_type": "test"}),
            ("cloudWatchLogEvent.json", {"func": None, "detail_type": "test"}),
            ("cloudWatchLogEventWithPolicyLevel.json", {"func": None, "detail_type": "test"}),
            ("cloudformationCustomResourceCreate.json", {"func": None, "detail_type": "test"}),
            ("cloudformationCustomResourceDelete.json", {"func": None, "detail_type": "test"}),
            ("cloudformationCustomResourceUpdate.json", {"func": None, "detail_type": "test"}),
            ("codeDeployLifecycleHookEvent.json", {"func": None, "detail_type": "test"}),
            ("codePipelineEvent.json", {"func": None, "detail_type": "test"}),
            ("codePipelineEventData.json", {"func": None, "detail_type": "test"}),
            ("codePipelineEventEmptyUserParameters.json", {"func": None, "detail_type": "test"}),
            ("codePipelineEventWithEncryptionKey.json", {"func": None, "detail_type": "test"}),
            ("cognitoCreateAuthChallengeEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoCustomEmailSenderEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoCustomMessageEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoCustomSMSSenderEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoDefineAuthChallengeEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoPostAuthenticationEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoPostConfirmationEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoPreAuthenticationEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoPreSignUpEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoPreTokenGenerationEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoPreTokenV2GenerationEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoUserMigrationEvent.json", {"func": None, "detail_type": "test"}),
            ("cognitoVerifyAuthChallengeResponseEvent.json", {"func": None, "detail_type": "test"}),
            ("connectContactFlowEventAll.json", {"func": None, "detail_type": "test"}),
            ("connectContactFlowEventMin.json", {"func": None, "detail_type": "test"}),
            ("dynamoStreamEvent.json", {"func": None, "detail_type": "test"}),
            ("kafkaEventMsk.json", {"func": None, "detail_type": "test"}),
            ("kafkaEventSelfManaged.json", {"func": None, "detail_type": "test"}),
            ("kinesisFirehoseKinesisEvent.json", {"func": None, "detail_type": "test"}),
            ("kinesisFirehosePutEvent.json", {"func": None, "detail_type": "test"}),
            ("kinesisFirehoseSQSEvent.json", {"func": None, "detail_type": "test"}),
            ("kinesisStreamCloudWatchLogsEvent.json", {"func": None, "detail_type": "test"}),
            ("kinesisStreamEvent.json", {"func": None, "detail_type": "test"}),
            ("kinesisStreamEventOneRecord.json", {"func": None, "detail_type": "test"}),
            ("lambdaFunctionUrlEvent.json", {"func": None, "detail_type": "test"}),
            ("lambdaFunctionUrlEventPathTrailingSlash.json", {"func": None, "detail_type": "test"}),
            ("lambdaFunctionUrlEventWithHeaders.json", {"func": None, "detail_type": "test"}),
            ("lambdaFunctionUrlIAMEvent.json", {"func": None, "detail_type": "test"}),
            ("rabbitMQEvent.json", {"func": None, "detail_type": "test"}),
            ("s3BatchOperationEventSchemaV1.json", {"func": None, "detail_type": "test"}),
            ("s3BatchOperationEventSchemaV2.json", {"func": None, "detail_type": "test"}),
            ("s3Event.json", {"func": None, "detail_type": "test"}),
            ("s3EventBridgeNotificationObjectCreatedEvent.json", {"func": None, "detail_type": "test"}),
            ("s3EventBridgeNotificationObjectDeletedEvent.json", {"func": None, "detail_type": "test"}),
            ("s3EventBridgeNotificationObjectExpiredEvent.json", {"func": None, "detail_type": "test"}),
            ("s3EventBridgeNotificationObjectRestoreCompletedEvent.json", {"func": None, "detail_type": "test"}),
            ("s3EventDecodedKey.json", {"func": None, "detail_type": "test"}),
            ("s3EventDeleteObject.json", {"func": None, "detail_type": "test"}),
            ("s3EventGlacier.json", {"func": None, "detail_type": "test"}),
            ("s3ObjectEventIAMUser.json", {"func": None, "detail_type": "test"}),
            ("s3ObjectEventTempCredentials.json", {"func": None, "detail_type": "test"}),
            ("s3SqsEvent.json", {"func": None, "detail_type": "test"}),
            ("secretsManagerEvent.json", {"func": None, "detail_type": "test"}),
            ("sesEvent.json", {"func": None, "detail_type": "test"}),
            ("snsEvent.json", {"func": None, "detail_type": "test"}),
            ("snsSqsEvent.json", {"func": None, "detail_type": "test"}),
            ("snsSqsFifoEvent.json", {"func": None, "detail_type": "test"}),
            ("sqsDlqTriggerEvent.json", {"func": None, "detail_type": "test"}),
            ("sqsEvent.json", {"func": None, "detail_type": "test"}),
            ("vpcLatticeEvent.json", {"func": None, "detail_type": "test"}),
            ("vpcLatticeEventPathTrailingSlash.json", {"func": None, "detail_type": "test"}),
            ("vpcLatticeEventV2PathTrailingSlash.json", {"func": None, "detail_type": "test"}),
            ("vpcLatticeV2Event.json", {"func": None, "detail_type": "test"}),
            ("vpcLatticeV2EventWithHeaders.json", {"func": None, "detail_type": "test"}),
            # eventBridgeEvent.json, not match (detail type, source, and resources)
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "source": "aws.lambda",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "source": "aws.lambda",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "source": "aws.ec2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "source": "aws.lambda",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "source": "aws.ec2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "source": "aws.lambda",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "source": "aws.ec2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            # eventBridgeEvent.json, not match (detail type and source)
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "source": "aws.lambda",
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "source": "aws.ec2",
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "source": "aws.lambda",
                },
            ),
            # eventBridgeEvent.json, not match (detail type and resources)
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification V2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "detail_type": "EC2 Instance State-change Notification",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            # eventBridgeEvent.json, not match (source and resources arguments)
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "source": "aws.lambda",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "source": "aws.lambda",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
                },
            ),
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "source": "aws.ec2",
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
            # eventBridgeEvent.json, not match detail_type
            ("eventBridgeEvent.json", {"func": None, "detail_type": "EC2 Instance State-change Notification V2"}),
            # eventBridgeEvent.json, not match source
            ("eventBridgeEvent.json", {"func": None, "source": "aws.lambda"}),
            # eventBridgeEvent.json, not match resources
            (
                "eventBridgeEvent.json",
                {
                    "func": None,
                    "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-9999999999abcdef9"],
                },
            ),
        ],
    )
    def test_match_false(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = EventBridgeRoute(**option_constructor)
        actual = route.match(event=event)
        assert actual is None
