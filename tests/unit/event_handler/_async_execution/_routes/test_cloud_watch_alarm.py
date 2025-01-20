import pytest

from aws_lambda_powertools.event_handler.async_execution.routes.cloud_watch_alarm import (
    CloudWatchAlarmRoute,
)
from aws_lambda_powertools.utilities.data_classes.cloud_watch_alarm_event import (
    CloudWatchAlarmEvent,
)
from tests.functional.utils import load_event


class TestCloudWatchAlarmRoute:
    def test_constructor_error(self):
        with pytest.raises(ValueError):
            CloudWatchAlarmRoute(func=None)

    @pytest.mark.parametrize(
        "option_constructor, option_func, expected",
        [
            (
                {"func": None, "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
                {"arn": None},
                False,
            ),
            (
                {"func": None, "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
                {"arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
                True,
            ),
            (
                {"func": None, "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.MainV2"},
                {"arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
                False,
            ),
            (
                {"func": None, "alarm_name": "SuppressionDemo.Main"},
                {"arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
                False,
            ),
        ],
    )
    def test_is_target_with_arn(self, option_constructor, option_func, expected):
        route = CloudWatchAlarmRoute(**option_constructor)
        actual = route.is_target_with_arn(**option_func)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option_func, expected",
        [
            ({"func": None, "alarm_name": "CompositeDemo.Main"}, {"alarm_name": None}, False),
            ({"func": None, "alarm_name": "CompositeDemo.Main"}, {"alarm_name": "CompositeDemo.Main"}, True),
            ({"func": None, "alarm_name": "CompositeDemo.MainV2"}, {"alarm_name": "CompositeDemo.Main"}, False),
            ({"func": None, "alarm_name_prefix": "CompositeDemo.M"}, {"alarm_name": "CompositeDemo.Main"}, True),
            ({"func": None, "alarm_name_prefix": "Main"}, {"alarm_name": "CompositeDemo.Main"}, False),
            (
                {"func": None, "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
                {"alarm_name": "CompositeDemo.Main"},
                False,
            ),
        ],
    )
    def test_is_target_with_alarm_name(self, option_constructor, option_func, expected):
        route = CloudWatchAlarmRoute(**option_constructor)
        actual = route.is_target_with_alarm_name(**option_func)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            # cloudWatchAlarmEventCompositeMetric.json, match arn, without alarm_name and alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {"func": lambda _: None, "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main"},
            ),
            # cloudWatchAlarmEventCompositeMetric.json, match arn, with alarm_name or alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main",
                    "alarm_name": "CompositeDemo.Main",
                },
            ),
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main",
                    "alarm_name_prefix": "CompositeD",
                },
            ),
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.Main",
                    "alarm_name": "CompositeDemo.Main",
                    "alarm_name_prefix": "CompositeD",
                },
            ),
            # cloudWatchAlarmEventCompositeMetric.json, match alarm_name, without alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": lambda _: None,
                    "alarm_name": "CompositeDemo.Main",
                },
            ),
            # cloudWatchAlarmEventCompositeMetric.json, match alarm_name, with alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": lambda _: None,
                    "alarm_name": "CompositeDemo.Main",
                    "alarm_name_prefix": "CompositeDD",
                },
            ),
            # cloudWatchAlarmEventCompositeMetric.json, match alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": lambda _: None,
                    "alarm_name_prefix": "CompositeD",
                },
            ),
            # cloudWatchAlarmEventSingleMetric.json, match arn, without alarm_name and alarm_name_prefix
            (
                "cloudWatchAlarmEventSingleMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:eu-west-1:912397435824:alarm:test_alarm",
                },
            ),
            # cloudWatchAlarmEventSingleMetric.json, match arn, with alarm_name or alarm_name_prefix
            (
                "cloudWatchAlarmEventSingleMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:eu-west-1:912397435824:alarm:test_alarm",
                    "alarm_name": "Test alert",
                },
            ),
            (
                "cloudWatchAlarmEventSingleMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:eu-west-1:912397435824:alarm:test_alarm",
                    "alarm_name_prefix": "Test a",
                },
            ),
            (
                "cloudWatchAlarmEventSingleMetric.json",
                {
                    "func": lambda _: None,
                    "arn": "arn:aws:cloudwatch:eu-west-1:912397435824:alarm:test_alarm",
                    "alarm_name": "Test alert",
                    "alarm_name_prefix": "Test a",
                },
            ),
            # cloudWatchAlarmEventSingleMetric.json, match alarm_name, without alarm_name_prefix
            ("cloudWatchAlarmEventSingleMetric.json", {"func": lambda _: None, "alarm_name": "Test alert"}),
            # cloudWatchAlarmEventSingleMetric.json, match alarm_name, with alarm_name_prefix
            (
                "cloudWatchAlarmEventSingleMetric.json",
                {"func": lambda _: None, "alarm_name": "Test alert", "alarm_name_prefix": "Test-a"},
            ),
            # cloudWatchAlarmEventSingleMetric.json, match alarm_name_prefix
            ("cloudWatchAlarmEventSingleMetric.json", {"func": lambda _: None, "alarm_name_prefix": "Test a"}),
        ],
    )
    def test_match_true(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = CloudWatchAlarmRoute(**option_constructor)
        expected = (route.func, CloudWatchAlarmEvent(event))
        actual = route.match(event=event)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            # other events
            ("activeMQEvent.json", {"func": None, "arn": "test"}),
            ("albEvent.json", {"func": None, "arn": "test"}),
            ("albEventPathTrailingSlash.json", {"func": None, "arn": "test"}),
            ("albMultiValueHeadersEvent.json", {"func": None, "arn": "test"}),
            ("albMultiValueQueryStringEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayAuthorizerRequestEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayAuthorizerTokenEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayAuthorizerV2Event.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyEventAnotherPath.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyEventNoOrigin.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyEventPathTrailingSlash.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyEventPrincipalId.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyEvent_noVersionAuth.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyOtherEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2Event.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2EventPathTrailingSlash.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2Event_GET.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2IamEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2LambdaAuthorizerEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2OtherGetEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2SchemaMiddlwareInvalidEvent.json", {"func": None, "arn": "test"}),
            ("apiGatewayProxyV2SchemaMiddlwareValidEvent.json", {"func": None, "arn": "test"}),
            ("apigatewayeSchemaMiddlwareInvalidEvent.json", {"func": None, "arn": "test"}),
            ("apigatewayeSchemaMiddlwareValidEvent.json", {"func": None, "arn": "test"}),
            ("appSyncAuthorizerEvent.json", {"func": None, "arn": "test"}),
            ("appSyncAuthorizerResponse.json", {"func": None, "arn": "test"}),
            ("appSyncBatchEvent.json", {"func": None, "arn": "test"}),
            ("appSyncDirectResolver.json", {"func": None, "arn": "test"}),
            ("appSyncResolverEvent.json", {"func": None, "arn": "test"}),
            ("awsConfigRuleConfigurationChanged.json", {"func": None, "arn": "test"}),
            ("awsConfigRuleOversizedConfiguration.json", {"func": None, "arn": "test"}),
            ("awsConfigRuleScheduled.json", {"func": None, "arn": "test"}),
            ("bedrockAgentEvent.json", {"func": None, "arn": "test"}),
            ("bedrockAgentEventWithPathParams.json", {"func": None, "arn": "test"}),
            ("bedrockAgentPostEvent.json", {"func": None, "arn": "test"}),
            ("cloudWatchDashboardEvent.json", {"func": None, "arn": "test"}),
            ("cloudWatchLogEvent.json", {"func": None, "arn": "test"}),
            ("cloudWatchLogEventWithPolicyLevel.json", {"func": None, "arn": "test"}),
            ("cloudformationCustomResourceCreate.json", {"func": None, "arn": "test"}),
            ("cloudformationCustomResourceDelete.json", {"func": None, "arn": "test"}),
            ("cloudformationCustomResourceUpdate.json", {"func": None, "arn": "test"}),
            ("codeDeployLifecycleHookEvent.json", {"func": None, "arn": "test"}),
            ("codePipelineEvent.json", {"func": None, "arn": "test"}),
            ("codePipelineEventData.json", {"func": None, "arn": "test"}),
            ("codePipelineEventEmptyUserParameters.json", {"func": None, "arn": "test"}),
            ("codePipelineEventWithEncryptionKey.json", {"func": None, "arn": "test"}),
            ("cognitoCreateAuthChallengeEvent.json", {"func": None, "arn": "test"}),
            ("cognitoCustomEmailSenderEvent.json", {"func": None, "arn": "test"}),
            ("cognitoCustomMessageEvent.json", {"func": None, "arn": "test"}),
            ("cognitoCustomSMSSenderEvent.json", {"func": None, "arn": "test"}),
            ("cognitoDefineAuthChallengeEvent.json", {"func": None, "arn": "test"}),
            ("cognitoPostAuthenticationEvent.json", {"func": None, "arn": "test"}),
            ("cognitoPostConfirmationEvent.json", {"func": None, "arn": "test"}),
            ("cognitoPreAuthenticationEvent.json", {"func": None, "arn": "test"}),
            ("cognitoPreSignUpEvent.json", {"func": None, "arn": "test"}),
            ("cognitoPreTokenGenerationEvent.json", {"func": None, "arn": "test"}),
            ("cognitoPreTokenV2GenerationEvent.json", {"func": None, "arn": "test"}),
            ("cognitoUserMigrationEvent.json", {"func": None, "arn": "test"}),
            ("cognitoVerifyAuthChallengeResponseEvent.json", {"func": None, "arn": "test"}),
            ("connectContactFlowEventAll.json", {"func": None, "arn": "test"}),
            ("connectContactFlowEventMin.json", {"func": None, "arn": "test"}),
            ("dynamoStreamEvent.json", {"func": None, "arn": "test"}),
            ("eventBridgeEvent.json", {"func": None, "arn": "test"}),
            ("kafkaEventMsk.json", {"func": None, "arn": "test"}),
            ("kafkaEventSelfManaged.json", {"func": None, "arn": "test"}),
            ("kinesisFirehoseKinesisEvent.json", {"func": None, "arn": "test"}),
            ("kinesisFirehosePutEvent.json", {"func": None, "arn": "test"}),
            ("kinesisFirehoseSQSEvent.json", {"func": None, "arn": "test"}),
            ("kinesisStreamCloudWatchLogsEvent.json", {"func": None, "arn": "test"}),
            ("kinesisStreamEvent.json", {"func": None, "arn": "test"}),
            ("kinesisStreamEventOneRecord.json", {"func": None, "arn": "test"}),
            ("lambdaFunctionUrlEvent.json", {"func": None, "arn": "test"}),
            ("lambdaFunctionUrlEventPathTrailingSlash.json", {"func": None, "arn": "test"}),
            ("lambdaFunctionUrlEventWithHeaders.json", {"func": None, "arn": "test"}),
            ("lambdaFunctionUrlIAMEvent.json", {"func": None, "arn": "test"}),
            ("rabbitMQEvent.json", {"func": None, "arn": "test"}),
            ("s3BatchOperationEventSchemaV1.json", {"func": None, "arn": "test"}),
            ("s3BatchOperationEventSchemaV2.json", {"func": None, "arn": "test"}),
            ("s3Event.json", {"func": None, "arn": "test"}),
            ("s3EventBridgeNotificationObjectCreatedEvent.json", {"func": None, "arn": "test"}),
            ("s3EventBridgeNotificationObjectDeletedEvent.json", {"func": None, "arn": "test"}),
            ("s3EventBridgeNotificationObjectExpiredEvent.json", {"func": None, "arn": "test"}),
            ("s3EventBridgeNotificationObjectRestoreCompletedEvent.json", {"func": None, "arn": "test"}),
            ("s3EventDecodedKey.json", {"func": None, "arn": "test"}),
            ("s3EventDeleteObject.json", {"func": None, "arn": "test"}),
            ("s3EventGlacier.json", {"func": None, "arn": "test"}),
            ("s3ObjectEventIAMUser.json", {"func": None, "arn": "test"}),
            ("s3ObjectEventTempCredentials.json", {"func": None, "arn": "test"}),
            ("s3SqsEvent.json", {"func": None, "arn": "test"}),
            ("secretsManagerEvent.json", {"func": None, "arn": "test"}),
            ("sesEvent.json", {"func": None, "arn": "test"}),
            ("snsEvent.json", {"func": None, "arn": "test"}),
            ("snsSqsEvent.json", {"func": None, "arn": "test"}),
            ("snsSqsFifoEvent.json", {"func": None, "arn": "test"}),
            ("sqsDlqTriggerEvent.json", {"func": None, "arn": "test"}),
            ("sqsEvent.json", {"func": None, "arn": "test"}),
            ("vpcLatticeEvent.json", {"func": None, "arn": "test"}),
            ("vpcLatticeEventPathTrailingSlash.json", {"func": None, "arn": "test"}),
            ("vpcLatticeEventV2PathTrailingSlash.json", {"func": None, "arn": "test"}),
            ("vpcLatticeV2Event.json", {"func": None, "arn": "test"}),
            ("vpcLatticeV2EventWithHeaders.json", {"func": None, "arn": "test"}),
            # cloudWatchAlarmEventCompositeMetric.json, not match arn, without alarm_name and alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {"func": None, "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.MainV2"},
            ),
            # cloudWatchAlarmEventCompositeMetric.json, not match arn, with alarm_name or alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": None,
                    "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.MainV2",
                    "alarm_name": "CompositeDemo.Main",
                },
            ),
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": None,
                    "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.MainV2",
                    "alarm_name_prefix": "CompositeD",
                },
            ),
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": None,
                    "arn": "arn:aws:cloudwatch:us-east-1:111122223333:alarm:SuppressionDemo.MainV2",
                    "alarm_name": "CompositeDemo.Main",
                    "alarm_name_prefix": "CompositeD",
                },
            ),
            # cloudWatchAlarmEventCompositeMetric.json, not match alarm_name, without alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": None,
                    "alarm_name": "CompositeDemo.MainV2",
                },
            ),
            # cloudWatchAlarmEventCompositeMetric.json, not match alarm_name, with alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": None,
                    "alarm_name": "CompositeDemo.MainV2",
                    "alarm_name_prefix": "CompositeD",
                },
            ),
            # cloudWatchAlarmEventCompositeMetric.json, not match alarm_name_prefix
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {
                    "func": None,
                    "alarm_name_prefix": "CompositeDD",
                },
            ),
        ],
    )
    def test_match_false(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = CloudWatchAlarmRoute(**option_constructor)
        actual = route.match(event=event)
        assert actual is None
