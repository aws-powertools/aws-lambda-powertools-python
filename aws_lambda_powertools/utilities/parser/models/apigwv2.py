from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field, validator
from pydantic.networks import IPvAnyNetwork

from aws_lambda_powertools.utilities.parser.types import Literal


class RequestContextV2AuthorizerIamCognito(BaseModel):
    amr: List[str]
    identityId: str
    identityPoolId: str


class RequestContextV2AuthorizerIam(BaseModel):
    accessKey: Optional[str] = None
    accountId: Optional[str] = None
    callerId: Optional[str] = None
    principalOrgId: Optional[str] = None
    userArn: Optional[str] = None
    userId: Optional[str] = None
    cognitoIdentity: Optional[RequestContextV2AuthorizerIamCognito] = None


class RequestContextV2AuthorizerJwt(BaseModel):
    claims: Dict[str, Any]
    scopes: List[str]


class RequestContextV2Authorizer(BaseModel):
    jwt: Optional[RequestContextV2AuthorizerJwt] = None
    iam: Optional[RequestContextV2AuthorizerIam] = None
    lambda_value: Union[Dict[str, Any], None] = Field(None, alias="lambda")


class RequestContextV2Http(BaseModel):
    method: Literal["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    path: str
    protocol: str
    sourceIp: IPvAnyNetwork
    userAgent: str


class RequestContextV2(BaseModel):
    accountId: str
    apiId: str
    authorizer: Optional[RequestContextV2Authorizer] = None
    domainName: str
    domainPrefix: str
    requestId: str
    routeKey: str
    stage: str
    time: str
    timeEpoch: datetime
    http: RequestContextV2Http

    # Validator to normalize the timeEpoch field
    # Converts the provided timestamp value to a UTC datetime object
    # See: https://github.com/pydantic/pydantic/issues/6518
    @validator("timeEpoch", pre=True)
    def normalize_timestamp(cls, value):
        date_utc = datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
        return date_utc


class APIGatewayProxyEventV2Model(BaseModel):
    version: str
    routeKey: str
    rawPath: str
    rawQueryString: str
    cookies: Optional[List[str]] = None
    headers: Dict[str, str]
    queryStringParameters: Optional[Dict[str, str]] = None
    pathParameters: Optional[Dict[str, str]] = None
    stageVariables: Optional[Dict[str, str]] = None
    requestContext: RequestContextV2
    body: Optional[Union[str, Type[BaseModel]]] = None
    isBase64Encoded: bool
