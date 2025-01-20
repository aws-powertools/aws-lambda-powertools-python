import pytest

from aws_lambda_powertools.event_handler.async_execution.routes.code_deploy_lifecycle_hook import (
    CodeDeployLifecycleHookRoute,
)
from aws_lambda_powertools.utilities.data_classes.code_deploy_lifecycle_hook_event import (
    CodeDeployLifecycleHookEvent,
)
from tests.functional.utils import load_event


class TestCodeDeployLifecycleHookRoute:
    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            ("codeDeployLifecycleHookEvent.json", {"func": None}),
        ],
    )
    def test_match_true(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = CodeDeployLifecycleHookRoute(**option_constructor)
        expected = (route.func, CodeDeployLifecycleHookEvent(event))
        actual = route.match(event=event)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor",
        [
            ("activeMQEvent.json", {"func": None}),
            ("albEvent.json", {"func": None}),
            ("albEventPathTrailingSlash.json", {"func": None}),
            ("albMultiValueHeadersEvent.json", {"func": None}),
            ("albMultiValueQueryStringEvent.json", {"func": None}),
            ("apiGatewayAuthorizerRequestEvent.json", {"func": None}),
            ("apiGatewayAuthorizerTokenEvent.json", {"func": None}),
            ("apiGatewayAuthorizerV2Event.json", {"func": None}),
            ("apiGatewayProxyEvent.json", {"func": None}),
            ("apiGatewayProxyEventAnotherPath.json", {"func": None}),
            ("apiGatewayProxyEventNoOrigin.json", {"func": None}),
            ("apiGatewayProxyEventPathTrailingSlash.json", {"func": None}),
            ("apiGatewayProxyEventPrincipalId.json", {"func": None}),
            ("apiGatewayProxyEvent_noVersionAuth.json", {"func": None}),
            ("apiGatewayProxyOtherEvent.json", {"func": None}),
            ("apiGatewayProxyV2Event.json", {"func": None}),
            ("apiGatewayProxyV2EventPathTrailingSlash.json", {"func": None}),
            ("apiGatewayProxyV2Event_GET.json", {"func": None}),
            ("apiGatewayProxyV2IamEvent.json", {"func": None}),
            ("apiGatewayProxyV2LambdaAuthorizerEvent.json", {"func": None}),
            ("apiGatewayProxyV2OtherGetEvent.json", {"func": None}),
            ("apiGatewayProxyV2SchemaMiddlwareInvalidEvent.json", {"func": None}),
            ("apiGatewayProxyV2SchemaMiddlwareValidEvent.json", {"func": None}),
            ("apigatewayeSchemaMiddlwareInvalidEvent.json", {"func": None}),
            ("apigatewayeSchemaMiddlwareValidEvent.json", {"func": None}),
            ("appSyncAuthorizerEvent.json", {"func": None}),
            ("appSyncAuthorizerResponse.json", {"func": None}),
            ("appSyncBatchEvent.json", {"func": None}),
            ("appSyncDirectResolver.json", {"func": None}),
            ("appSyncResolverEvent.json", {"func": None}),
            ("awsConfigRuleConfigurationChanged.json", {"func": None}),
            ("awsConfigRuleOversizedConfiguration.json", {"func": None}),
            ("awsConfigRuleScheduled.json", {"func": None}),
            ("bedrockAgentEvent.json", {"func": None}),
            ("bedrockAgentEventWithPathParams.json", {"func": None}),
            ("bedrockAgentPostEvent.json", {"func": None}),
            ("cloudWatchAlarmEventCompositeMetric.json", {"func": None}),
            ("cloudWatchAlarmEventSingleMetric.json", {"func": None}),
            ("cloudWatchDashboardEvent.json", {"func": None}),
            ("cloudWatchLogEvent.json", {"func": None}),
            ("cloudWatchLogEventWithPolicyLevel.json", {"func": None}),
            ("cloudformationCustomResourceCreate.json", {"func": None}),
            ("cloudformationCustomResourceDelete.json", {"func": None}),
            ("cloudformationCustomResourceUpdate.json", {"func": None}),
            ("codePipelineEvent.json", {"func": None}),
            ("codePipelineEventData.json", {"func": None}),
            ("codePipelineEventEmptyUserParameters.json", {"func": None}),
            ("codePipelineEventWithEncryptionKey.json", {"func": None}),
            ("cognitoCreateAuthChallengeEvent.json", {"func": None}),
            ("cognitoCustomEmailSenderEvent.json", {"func": None}),
            ("cognitoCustomMessageEvent.json", {"func": None}),
            ("cognitoCustomSMSSenderEvent.json", {"func": None}),
            ("cognitoDefineAuthChallengeEvent.json", {"func": None}),
            ("cognitoPostAuthenticationEvent.json", {"func": None}),
            ("cognitoPostConfirmationEvent.json", {"func": None}),
            ("cognitoPreAuthenticationEvent.json", {"func": None}),
            ("cognitoPreSignUpEvent.json", {"func": None}),
            ("cognitoPreTokenGenerationEvent.json", {"func": None}),
            ("cognitoPreTokenV2GenerationEvent.json", {"func": None}),
            ("cognitoUserMigrationEvent.json", {"func": None}),
            ("cognitoVerifyAuthChallengeResponseEvent.json", {"func": None}),
            ("connectContactFlowEventAll.json", {"func": None}),
            ("connectContactFlowEventMin.json", {"func": None}),
            ("dynamoStreamEvent.json", {"func": None}),
            ("eventBridgeEvent.json", {"func": None}),
            ("kafkaEventMsk.json", {"func": None}),
            ("kafkaEventSelfManaged.json", {"func": None}),
            ("kinesisFirehoseKinesisEvent.json", {"func": None}),
            ("kinesisFirehosePutEvent.json", {"func": None}),
            ("kinesisFirehoseSQSEvent.json", {"func": None}),
            ("kinesisStreamCloudWatchLogsEvent.json", {"func": None}),
            ("kinesisStreamEvent.json", {"func": None}),
            ("kinesisStreamEventOneRecord.json", {"func": None}),
            ("lambdaFunctionUrlEvent.json", {"func": None}),
            ("lambdaFunctionUrlEventPathTrailingSlash.json", {"func": None}),
            ("lambdaFunctionUrlEventWithHeaders.json", {"func": None}),
            ("lambdaFunctionUrlIAMEvent.json", {"func": None}),
            ("rabbitMQEvent.json", {"func": None}),
            ("s3BatchOperationEventSchemaV1.json", {"func": None}),
            ("s3BatchOperationEventSchemaV2.json", {"func": None}),
            ("s3Event.json", {"func": None}),
            ("s3EventBridgeNotificationObjectCreatedEvent.json", {"func": None}),
            ("s3EventBridgeNotificationObjectDeletedEvent.json", {"func": None}),
            ("s3EventBridgeNotificationObjectExpiredEvent.json", {"func": None}),
            ("s3EventBridgeNotificationObjectRestoreCompletedEvent.json", {"func": None}),
            ("s3EventDecodedKey.json", {"func": None}),
            ("s3EventDeleteObject.json", {"func": None}),
            ("s3EventGlacier.json", {"func": None}),
            ("s3ObjectEventIAMUser.json", {"func": None}),
            ("s3ObjectEventTempCredentials.json", {"func": None}),
            ("s3SqsEvent.json", {"func": None}),
            ("secretsManagerEvent.json", {"func": None}),
            ("sesEvent.json", {"func": None}),
            ("snsEvent.json", {"func": None}),
            ("snsSqsEvent.json", {"func": None}),
            ("snsSqsFifoEvent.json", {"func": None}),
            ("sqsDlqTriggerEvent.json", {"func": None}),
            ("sqsEvent.json", {"func": None}),
            ("vpcLatticeEvent.json", {"func": None}),
            ("vpcLatticeEventPathTrailingSlash.json", {"func": None}),
            ("vpcLatticeEventV2PathTrailingSlash.json", {"func": None}),
            ("vpcLatticeV2Event.json", {"func": None}),
            ("vpcLatticeV2EventWithHeaders.json", {"func": None}),
        ],
    )
    def test_match_false(self, event_name, option_constructor):
        event = load_event(file_name=event_name)
        route = CodeDeployLifecycleHookRoute(**option_constructor)
        actual = route.match(event=event)
        assert actual is None
