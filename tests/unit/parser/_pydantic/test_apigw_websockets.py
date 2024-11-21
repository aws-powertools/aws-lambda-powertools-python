from aws_lambda_powertools.utilities.parser import envelopes, parse
from aws_lambda_powertools.utilities.parser.models import (
    APIGatewayWebSocketConnectEventModel,
    APIGatewayWebSocketDisconnectEventModel,
    APIGatewayWebSocketMessageEventModel,
)
from tests.functional.utils import load_event
from tests.unit.parser._pydantic.schemas import MyApiGatewayWebSocketBusiness


def test_apigw_websocket_api_message_event_with_envelope():
    raw_event = load_event("apiGatewayWebSocketApiMessage.json")
    raw_event["body"] = '{"action": "chat", "message": "Hello Ran"}'
    parsed_event: MyApiGatewayWebSocketBusiness = parse(
        event=raw_event,
        model=MyApiGatewayWebSocketBusiness,
        envelope=envelopes.ApiGatewayWebSocketEnvelope,
    )

    assert parsed_event.message == "Hello Ran"
    assert parsed_event.action == "chat"


def test_apigw_websocket_api_message_event():
    raw_event = load_event("apiGatewayWebSocketApiMessage.json")
    parsed_event: APIGatewayWebSocketMessageEventModel = APIGatewayWebSocketMessageEventModel(**raw_event)

    request_context = parsed_event.requestContext
    assert request_context.apiId == raw_event["requestContext"]["apiId"]
    assert request_context.domainName == raw_event["requestContext"]["domainName"]
    assert request_context.extendedRequestId == raw_event["requestContext"]["extendedRequestId"]

    identity = request_context.identity
    assert str(identity.sourceIp) == f'{raw_event["requestContext"]["identity"]["sourceIp"]}/32'

    assert request_context.requestId == raw_event["requestContext"]["requestId"]
    assert request_context.requestTime == raw_event["requestContext"]["requestTime"]
    convert_time = int(round(request_context.requestTimeEpoch.timestamp() * 1000))
    assert convert_time == 1731332746514
    assert request_context.stage == raw_event["requestContext"]["stage"]
    convert_time = int(round(request_context.connectedAt.timestamp() * 1000))
    assert convert_time == 1731332735513
    assert request_context.connectionId == raw_event["requestContext"]["connectionId"]
    assert request_context.eventType == raw_event["requestContext"]["eventType"]
    assert request_context.messageDirection == raw_event["requestContext"]["messageDirection"]
    assert request_context.messageId == raw_event["requestContext"]["messageId"]
    assert request_context.routeKey == raw_event["requestContext"]["routeKey"]

    assert parsed_event.body == raw_event["body"]
    assert parsed_event.isBase64Encoded == raw_event["isBase64Encoded"]


# not sure you can send an empty body TBH but it was a test in api gw so i kept it here, needs verification
def test_apigw_websocket_api_message_event_empty_body():
    event = load_event("apiGatewayWebSocketApiMessage.json")
    event["body"] = None
    parse(event=event, model=APIGatewayWebSocketMessageEventModel)


def test_apigw_websocket_api_connect_event():
    raw_event = load_event("apiGatewayWebSocketApiConnect.json")
    parsed_event: APIGatewayWebSocketConnectEventModel = APIGatewayWebSocketConnectEventModel(**raw_event)

    request_context = parsed_event.requestContext
    assert request_context.apiId == raw_event["requestContext"]["apiId"]
    assert request_context.domainName == raw_event["requestContext"]["domainName"]
    assert request_context.extendedRequestId == raw_event["requestContext"]["extendedRequestId"]

    identity = request_context.identity
    assert str(identity.sourceIp) == f'{raw_event["requestContext"]["identity"]["sourceIp"]}/32'

    assert request_context.requestId == raw_event["requestContext"]["requestId"]
    assert request_context.requestTime == raw_event["requestContext"]["requestTime"]
    convert_time = int(round(request_context.requestTimeEpoch.timestamp() * 1000))
    assert convert_time == 1731324924561
    assert request_context.stage == raw_event["requestContext"]["stage"]
    convert_time = int(round(request_context.connectedAt.timestamp() * 1000))
    assert convert_time == 1731324924553
    assert request_context.connectionId == raw_event["requestContext"]["connectionId"]
    assert request_context.eventType == raw_event["requestContext"]["eventType"]
    assert request_context.messageDirection == raw_event["requestContext"]["messageDirection"]
    assert request_context.routeKey == raw_event["requestContext"]["routeKey"]

    assert parsed_event.isBase64Encoded == raw_event["isBase64Encoded"]
    assert parsed_event.headers == raw_event["headers"]
    assert parsed_event.multiValueHeaders == raw_event["multiValueHeaders"]


def test_apigw_websocket_api_disconnect_event():
    raw_event = load_event("apiGatewayWebSocketApiDisconnect.json")
    parsed_event: APIGatewayWebSocketDisconnectEventModel = APIGatewayWebSocketDisconnectEventModel(**raw_event)

    request_context = parsed_event.requestContext
    assert request_context.apiId == raw_event["requestContext"]["apiId"]
    assert request_context.domainName == raw_event["requestContext"]["domainName"]
    assert request_context.extendedRequestId == raw_event["requestContext"]["extendedRequestId"]

    identity = request_context.identity
    assert str(identity.sourceIp) == f'{raw_event["requestContext"]["identity"]["sourceIp"]}/32'

    assert request_context.requestId == raw_event["requestContext"]["requestId"]
    assert request_context.requestTime == raw_event["requestContext"]["requestTime"]
    convert_time = int(round(request_context.requestTimeEpoch.timestamp() * 1000))
    assert convert_time == 1731333109875
    assert request_context.stage == raw_event["requestContext"]["stage"]
    convert_time = int(round(request_context.connectedAt.timestamp() * 1000))
    assert convert_time == 1731332735513
    assert request_context.connectionId == raw_event["requestContext"]["connectionId"]
    assert request_context.eventType == raw_event["requestContext"]["eventType"]
    assert request_context.messageDirection == raw_event["requestContext"]["messageDirection"]
    assert request_context.routeKey == raw_event["requestContext"]["routeKey"]
    assert request_context.disconnectReason == raw_event["requestContext"]["disconnectReason"]
    assert request_context.disconnectStatusCode == raw_event["requestContext"]["disconnectStatusCode"]

    assert parsed_event.isBase64Encoded == raw_event["isBase64Encoded"]
    assert parsed_event.headers == raw_event["headers"]
    assert parsed_event.multiValueHeaders == raw_event["multiValueHeaders"]
