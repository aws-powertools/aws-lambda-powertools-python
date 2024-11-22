from datetime import datetime
from typing import Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel
from pydantic.networks import IPvAnyNetwork


class APIGatewayWebSocketEventIdentity(BaseModel):
    sourceIp: IPvAnyNetwork
    userAgent: Optional[str]

class APIGatewayWebSocketEventRequestContextBase(BaseModel):
    extendedRequestId: str
    requestTime: str
    stage: str
    connectedAt: datetime
    requestTimeEpoch: datetime
    identity: APIGatewayWebSocketEventIdentity
    requestId: str
    domainName: str
    connectionId: str
    apiId: str


class APIGatewayWebSocketMessageEventRequestContext(APIGatewayWebSocketEventRequestContextBase):
    routeKey: str
    messageId: str
    eventType: Literal["MESSAGE"]
    messageDirection: Literal["IN", "OUT"]


class APIGatewayWebSocketConnectEventRequestContext(APIGatewayWebSocketEventRequestContextBase):
    routeKey: Literal["$connect"]
    eventType: Literal["CONNECT"]
    messageDirection: Literal["IN"]


class APIGatewayWebSocketDisconnectEventRequestContext(APIGatewayWebSocketEventRequestContextBase):
    routeKey: Literal["$disconnect"]
    disconnectStatusCode: int
    eventType: Literal["DISCONNECT"]
    messageDirection: Literal["IN"]
    disconnectReason: str


class APIGatewayWebSocketConnectEventModel(BaseModel):
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]]
    requestContext: APIGatewayWebSocketConnectEventRequestContext
    isBase64Encoded: bool


class APIGatewayWebSocketDisconnectEventModel(BaseModel):
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]]
    requestContext: APIGatewayWebSocketDisconnectEventRequestContext
    isBase64Encoded: bool


class APIGatewayWebSocketMessageEventModel(BaseModel):
    requestContext: APIGatewayWebSocketMessageEventRequestContext
    isBase64Encoded: bool
    body: Optional[Union[str, Type[BaseModel]]] = None
