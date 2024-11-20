from datetime import datetime
from typing import Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel
from pydantic.networks import IPvAnyNetwork


class APIGatewayWebSocketApiEventIdentity(BaseModel):
    sourceIp: IPvAnyNetwork


class APIGatewayWebSocketApiEventRequestContextBase(BaseModel):
    extendedRequestId: str
    requestTime: str
    stage: str
    connectedAt: datetime
    requestTimeEpoch: datetime
    identity: APIGatewayWebSocketApiEventIdentity
    requestId: str
    domainName: str
    connectionId: str
    apiId: str


class APIGatewayWebSocketApiMessageEventRequestContext(APIGatewayWebSocketApiEventRequestContextBase):
    routeKey: str
    messageId: str
    eventType: Literal["MESSAGE"]
    messageDirection: Literal["IN", "OUT"]


class APIGatewayWebSocketApiConnectEventRequestContext(APIGatewayWebSocketApiEventRequestContextBase):
    routeKey: Literal["$connect"]
    eventType: Literal["CONNECT"]
    messageDirection: Literal["IN"]


class APIGatewayWebSocketApiDisconnectEventRequestContext(APIGatewayWebSocketApiEventRequestContextBase):
    routeKey: Literal["$disconnect"]
    disconnectStatusCode: int
    eventType: Literal["DISCONNECT"]
    messageDirection: Literal["IN"]
    disconnectReason: str


class APIGatewayWebSocketApiConnectEventModel(BaseModel):
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]]
    requestContext: APIGatewayWebSocketApiConnectEventRequestContext
    isBase64Encoded: bool


class APIGatewayWebSocketApiDisconnectEventModel(BaseModel):
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]]
    requestContext: APIGatewayWebSocketApiDisconnectEventRequestContext
    isBase64Encoded: bool


class APIGatewayWebSocketApiMessageEventModel(BaseModel):
    requestContext: APIGatewayWebSocketApiMessageEventRequestContext
    isBase64Encoded: bool
    body: Optional[Union[str, Type[BaseModel]]] = None
