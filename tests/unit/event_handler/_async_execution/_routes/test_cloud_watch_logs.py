import pytest

from aws_lambda_powertools.event_handler.async_execution.routes.cloud_watch_logs import (
    CloudWatchLogsRoute,
)
from aws_lambda_powertools.utilities.data_classes.cloud_watch_logs_event import (
    CloudWatchLogsEvent,
)
from tests.functional.utils import load_event


class TestCloudWatchLogsRoute:
    def test_constructor_error(self):
        with pytest.raises(ValueError):
            CloudWatchLogsRoute(func=None)

    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"func": None, "log_group": "test"},
                {
                    "func": None,
                    "log_group": "test",
                    "log_group_prefix": None,
                    "log_stream": None,
                    "log_stream_prefix": None,
                    "subscription_filters": None,
                },
            ),
            (
                {"func": None, "log_group_prefix": "test"},
                {
                    "func": None,
                    "log_group": None,
                    "log_group_prefix": "test",
                    "log_stream": None,
                    "log_stream_prefix": None,
                    "subscription_filters": None,
                },
            ),
            (
                {"func": None, "log_stream": "test"},
                {
                    "func": None,
                    "log_group": None,
                    "log_group_prefix": None,
                    "log_stream": "test",
                    "log_stream_prefix": None,
                    "subscription_filters": None,
                },
            ),
            (
                {"func": None, "log_stream_prefix": "test"},
                {
                    "func": None,
                    "log_group": None,
                    "log_group_prefix": None,
                    "log_stream": None,
                    "log_stream_prefix": "test",
                    "subscription_filters": None,
                },
            ),
            (
                {"func": None, "subscription_filters": "test"},
                {
                    "func": None,
                    "log_group": None,
                    "log_group_prefix": None,
                    "log_stream": None,
                    "log_stream_prefix": None,
                    "subscription_filters": ["test"],
                },
            ),
            (
                {"func": None, "subscription_filters": ["test", "name"]},
                {
                    "func": None,
                    "log_group": None,
                    "log_group_prefix": None,
                    "log_stream": None,
                    "log_stream_prefix": None,
                    "subscription_filters": ["test", "name"],
                },
            ),
        ],
    )
    def test_constructor_normal(self, option, expected):
        route = CloudWatchLogsRoute(**option)
        assert route.__dict__ == expected

    @pytest.mark.parametrize(
        "option_constructor, option, expected",
        [
            ({"func": None, "log_group": "test-log-group"}, {"log_group": None}, False),
            ({"func": None, "log_group": "test-log-group"}, {"log_group": "test-log-group-v2"}, False),
            ({"func": None, "log_group": "test-log-group"}, {"log_group": "test-log-group"}, True),
            ({"func": None, "log_group_prefix": "test-ll"}, {"log_group": "test-log-group"}, False),
            ({"func": None, "log_group_prefix": "est-l"}, {"log_group": "test-log-group"}, False),
            ({"func": None, "log_group_prefix": "test-l"}, {"log_group": "test-log-group"}, True),
            ({"func": None, "log_stream": "test-log-group"}, {"log_group": None}, False),
        ],
    )
    def test_is_target_with_log_group(self, option_constructor, option, expected):
        route = CloudWatchLogsRoute(**option_constructor)
        actual = route.is_target_with_log_group(**option)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option, expected",
        [
            ({"func": None, "log_stream": "test-log-stream"}, {"log_stream": None}, False),
            ({"func": None, "log_stream": "test-log-stream-v2"}, {"log_stream": "test-log-stream"}, False),
            ({"func": None, "log_stream": "test-log-stream"}, {"log_stream": "test-log-stream"}, True),
            ({"func": None, "log_stream_prefix": "test-ll"}, {"log_stream": "test-log-stream"}, False),
            ({"func": None, "log_stream_prefix": "est-l"}, {"log_stream": "test-log-stream"}, False),
            ({"func": None, "log_stream_prefix": "test-l"}, {"log_stream": "test-log-stream"}, True),
            ({"func": None, "log_group": "test-l"}, {"log_stream": "test-log-stream"}, False),
        ],
    )
    def test_is_target_with_log_stream(self, option_constructor, option, expected):
        route = CloudWatchLogsRoute(**option_constructor)
        actual = route.is_target_with_log_stream(**option)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option, expected",
        [
            ({"func": None, "subscription_filters": ["test"]}, {"subscription_filters": None}, False),
            ({"func": None, "log_group": "test"}, {"subscription_filters": ["test"]}, False),
            ({"func": None, "subscription_filters": ["test"]}, {"subscription_filters": ["test"]}, True),
            ({"func": None, "subscription_filters": ["test", "name"]}, {"subscription_filters": ["test"]}, True),
            ({"func": None, "subscription_filters": ["test"]}, {"subscription_filters": ["test", "name"]}, True),
            ({"func": None, "subscription_filters": ["test"]}, {"subscription_filters": ["name"]}, False),
        ],
    )
    def test_is_target_with_subscription_filters(self, option_constructor, option, expected):
        route = CloudWatchLogsRoute(**option_constructor)
        actual = route.is_target_with_subscription_filters(**option)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream_prefix": "testLogS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream_prefix": "testLogS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStream",
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream": "testLogStream",
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream_prefix": "testLogS",
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream_prefix": "testLogS",
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": lambda *_: None, "log_group": "testLogGroup", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": lambda *_: None, "log_group_prefix": "testLogG", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": lambda *_: None, "log_stream": "testLogStream", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": lambda *_: None, "log_stream_prefix": "testLogS", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": lambda *_: None,
                    "log_stream": "testLogStream",
                },
            ),
            ("cloudWatchLogEvent.json", {"func": lambda *_: None, "subscription_filters": ["testFilter"]}),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream_prefix": "testLogS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream_prefix": "testLogS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStream",
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream": "testLogStream",
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "log_stream_prefix": "testLogS",
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "log_stream_prefix": "testLogS",
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group": "testLogGroup",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_group_prefix": "testLogG",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {
                    "func": lambda *_: None,
                    "log_stream_prefix": "testLogS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {"func": lambda *_: None, "log_group": "testLogGroup"},
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {"func": lambda *_: None, "log_group_prefix": "testLogG"},
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {"func": lambda *_: None, "log_stream": "testLogStream"},
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {"func": lambda *_: None, "log_stream_prefix": "testLogS"},
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {"func": lambda *_: None, "subscription_filters": ["testFilter"]},
            ),
        ],
    )
    def test_match_true(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = CloudWatchLogsRoute(**option_constructor)
        expected = (route.func, CloudWatchLogsEvent(event))
        actual = route.match(event=event)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            ("activeMQEvent.json", {"func": None, "log_group": "test"}),
            ("albEvent.json", {"func": None, "log_group": "test"}),
            ("albEventPathTrailingSlash.json", {"func": None, "log_group": "test"}),
            ("albMultiValueHeadersEvent.json", {"func": None, "log_group": "test"}),
            ("albMultiValueQueryStringEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayAuthorizerRequestEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayAuthorizerTokenEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayAuthorizerV2Event.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyEventAnotherPath.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyEventNoOrigin.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyEventPathTrailingSlash.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyEventPrincipalId.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyEvent_noVersionAuth.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyOtherEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2Event.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2EventPathTrailingSlash.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2Event_GET.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2IamEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2LambdaAuthorizerEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2OtherGetEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2SchemaMiddlwareInvalidEvent.json", {"func": None, "log_group": "test"}),
            ("apiGatewayProxyV2SchemaMiddlwareValidEvent.json", {"func": None, "log_group": "test"}),
            ("apigatewayeSchemaMiddlwareInvalidEvent.json", {"func": None, "log_group": "test"}),
            ("apigatewayeSchemaMiddlwareValidEvent.json", {"func": None, "log_group": "test"}),
            ("appSyncAuthorizerEvent.json", {"func": None, "log_group": "test"}),
            ("appSyncAuthorizerResponse.json", {"func": None, "log_group": "test"}),
            ("appSyncBatchEvent.json", {"func": None, "log_group": "test"}),
            ("appSyncDirectResolver.json", {"func": None, "log_group": "test"}),
            ("appSyncResolverEvent.json", {"func": None, "log_group": "test"}),
            ("awsConfigRuleConfigurationChanged.json", {"func": None, "log_group": "test"}),
            ("awsConfigRuleOversizedConfiguration.json", {"func": None, "log_group": "test"}),
            ("awsConfigRuleScheduled.json", {"func": None, "log_group": "test"}),
            ("bedrockAgentEvent.json", {"func": None, "log_group": "test"}),
            ("bedrockAgentEventWithPathParams.json", {"func": None, "log_group": "test"}),
            ("bedrockAgentPostEvent.json", {"func": None, "log_group": "test"}),
            ("cloudWatchAlarmEventCompositeMetric.json", {"func": None, "log_group": "test"}),
            ("cloudWatchAlarmEventSingleMetric.json", {"func": None, "log_group": "test"}),
            ("cloudWatchDashboardEvent.json", {"func": None, "log_group": "test"}),
            ("cloudformationCustomResourceCreate.json", {"func": None, "log_group": "test"}),
            ("cloudformationCustomResourceDelete.json", {"func": None, "log_group": "test"}),
            ("cloudformationCustomResourceUpdate.json", {"func": None, "log_group": "test"}),
            ("codeDeployLifecycleHookEvent.json", {"func": None, "log_group": "test"}),
            ("codePipelineEvent.json", {"func": None, "log_group": "test"}),
            ("codePipelineEventData.json", {"func": None, "log_group": "test"}),
            ("codePipelineEventEmptyUserParameters.json", {"func": None, "log_group": "test"}),
            ("codePipelineEventWithEncryptionKey.json", {"func": None, "log_group": "test"}),
            ("cognitoCreateAuthChallengeEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoCustomEmailSenderEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoCustomMessageEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoCustomSMSSenderEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoDefineAuthChallengeEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoPostAuthenticationEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoPostConfirmationEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoPreAuthenticationEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoPreSignUpEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoPreTokenGenerationEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoPreTokenV2GenerationEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoUserMigrationEvent.json", {"func": None, "log_group": "test"}),
            ("cognitoVerifyAuthChallengeResponseEvent.json", {"func": None, "log_group": "test"}),
            ("connectContactFlowEventAll.json", {"func": None, "log_group": "test"}),
            ("connectContactFlowEventMin.json", {"func": None, "log_group": "test"}),
            ("dynamoStreamEvent.json", {"func": None, "log_group": "test"}),
            ("eventBridgeEvent.json", {"func": None, "log_group": "test"}),
            ("kafkaEventMsk.json", {"func": None, "log_group": "test"}),
            ("kafkaEventSelfManaged.json", {"func": None, "log_group": "test"}),
            ("kinesisFirehoseKinesisEvent.json", {"func": None, "log_group": "test"}),
            ("kinesisFirehosePutEvent.json", {"func": None, "log_group": "test"}),
            ("kinesisFirehoseSQSEvent.json", {"func": None, "log_group": "test"}),
            ("kinesisStreamCloudWatchLogsEvent.json", {"func": None, "log_group": "test"}),
            ("kinesisStreamEvent.json", {"func": None, "log_group": "test"}),
            ("kinesisStreamEventOneRecord.json", {"func": None, "log_group": "test"}),
            ("lambdaFunctionUrlEvent.json", {"func": None, "log_group": "test"}),
            ("lambdaFunctionUrlEventPathTrailingSlash.json", {"func": None, "log_group": "test"}),
            ("lambdaFunctionUrlEventWithHeaders.json", {"func": None, "log_group": "test"}),
            ("lambdaFunctionUrlIAMEvent.json", {"func": None, "log_group": "test"}),
            ("rabbitMQEvent.json", {"func": None, "log_group": "test"}),
            ("s3BatchOperationEventSchemaV1.json", {"func": None, "log_group": "test"}),
            ("s3BatchOperationEventSchemaV2.json", {"func": None, "log_group": "test"}),
            ("s3Event.json", {"func": None, "log_group": "test"}),
            ("s3EventBridgeNotificationObjectCreatedEvent.json", {"func": None, "log_group": "test"}),
            ("s3EventBridgeNotificationObjectDeletedEvent.json", {"func": None, "log_group": "test"}),
            ("s3EventBridgeNotificationObjectExpiredEvent.json", {"func": None, "log_group": "test"}),
            ("s3EventBridgeNotificationObjectRestoreCompletedEvent.json", {"func": None, "log_group": "test"}),
            ("s3EventDecodedKey.json", {"func": None, "log_group": "test"}),
            ("s3EventDeleteObject.json", {"func": None, "log_group": "test"}),
            ("s3EventGlacier.json", {"func": None, "log_group": "test"}),
            ("s3ObjectEventIAMUser.json", {"func": None, "log_group": "test"}),
            ("s3ObjectEventTempCredentials.json", {"func": None, "log_group": "test"}),
            ("s3SqsEvent.json", {"func": None, "log_group": "test"}),
            ("secretsManagerEvent.json", {"func": None, "log_group": "test"}),
            ("sesEvent.json", {"func": None, "log_group": "test"}),
            ("snsEvent.json", {"func": None, "log_group": "test"}),
            ("snsSqsEvent.json", {"func": None, "log_group": "test"}),
            ("snsSqsFifoEvent.json", {"func": None, "log_group": "test"}),
            ("sqsDlqTriggerEvent.json", {"func": None, "log_group": "test"}),
            ("sqsEvent.json", {"func": None, "log_group": "test"}),
            ("vpcLatticeEvent.json", {"func": None, "log_group": "test"}),
            ("vpcLatticeEventPathTrailingSlash.json", {"func": None, "log_group": "test"}),
            ("vpcLatticeEventV2PathTrailingSlash.json", {"func": None, "log_group": "test"}),
            ("vpcLatticeV2Event.json", {"func": None, "log_group": "test"}),
            ("vpcLatticeV2EventWithHeaders.json", {"func": None, "log_group": "test"}),
            # cloudWatchLogEvent.json, not match (log group, log stream and subscription filters)
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroupV2",
                    "log_stream": "testLogStreamV2",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group_prefix": "testLogGG",
                    "log_stream": "testLogStreamV2",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroupV2",
                    "log_stream_prefix": "testLogSS",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group_prefix": "testLogGG",
                    "log_stream_prefix": "testLogSS",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroupV2",
                    "log_stream": "testLogStreamV2",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group_prefix": "testLogGG",
                    "log_stream": "testLogStreamV2",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroupV2",
                    "log_stream_prefix": "testLogSS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group_prefix": "testLogGG",
                    "log_stream_prefix": "testLogSS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroupV2",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group_prefix": "testLogGG",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStreamV2",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroup",
                    "log_stream_prefix": "testLogSS",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroupV2",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group_prefix": "testLogGG",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStreamV2",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroup",
                    "log_stream_prefix": "testLogSS",
                    "subscription_filters": ["testFilter"],
                },
            ),
            (
                "cloudWatchLogEvent.json",
                {
                    "func": None,
                    "log_group": "testLogGroup",
                    "log_stream": "testLogStream",
                    "subscription_filters": ["testFilterV2"],
                },
            ),
            # cloudWatchLogEvent.json, not match (log group and log stream)
            ("cloudWatchLogEvent.json", {"func": None, "log_group": "testLogGroupV2", "log_stream": "testLogStreamV2"}),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group_prefix": "testLogGG", "log_stream": "testLogStreamV2"},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group": "testLogGroupV2", "log_stream_prefix": "testLogSS"},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group_prefix": "testLogGG", "log_stream_prefix": "testLogSS"},
            ),
            ("cloudWatchLogEvent.json", {"func": None, "log_group": "testLogGroupV2", "log_stream": "testLogStream"}),
            ("cloudWatchLogEvent.json", {"func": None, "log_group_prefix": "testLogGG", "log_stream": "testLogStream"}),
            ("cloudWatchLogEvent.json", {"func": None, "log_group": "testLogGroup", "log_stream": "testLogStreamV2"}),
            ("cloudWatchLogEvent.json", {"func": None, "log_group": "testLogGroup", "log_stream_prefix": "testLogSS"}),
            # cloudWatchLogEvent.json, not match (log group and subscription filters)
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group": "testLogGroupV2", "subscription_filters": ["testFilterV2"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group_prefix": "testLogGG", "subscription_filters": ["testFilterV2"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group": "testLogGroupV2", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group_prefix": "testLogGG", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_group": "testLogGroup", "subscription_filters": ["testFilterV2"]},
            ),
            # cloudWatchLogEvent.json, not match (log stream and subscription filters)
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_stream": "testLogStreamV2", "subscription_filters": ["testFilterV2"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_stream_prefix": "testLogSS", "subscription_filters": ["testFilterV2"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_stream": "testLogStreamV2", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_stream_prefix": "testLogSS", "subscription_filters": ["testFilter"]},
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "log_stream": "testLogStream", "subscription_filters": ["testFilterV2"]},
            ),
            # cloudWatchLogEvent.json, not match log_group
            ("cloudWatchLogEvent.json", {"func": None, "log_group": "testLogGroupV2"}),
            ("cloudWatchLogEvent.json", {"func": None, "log_group_prefix": "testLogGG"}),
            # cloudWatchLogEvent.json, not match log_stream
            ("cloudWatchLogEvent.json", {"func": None, "log_stream": "testLogStreamV2"}),
            ("cloudWatchLogEvent.json", {"func": None, "log_stream_prefix": "testLogSS"}),
            # cloudWatchLogEvent.json, not match subscription_filters
            ("cloudWatchLogEvent.json", {"func": None, "subscription_filters": ["testFilterV2"]}),
        ],
    )
    def test_match_false(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = CloudWatchLogsRoute(**option_constructor)
        actual = route.match(event=event)
        assert actual is None
