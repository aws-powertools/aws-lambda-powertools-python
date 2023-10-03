from datetime import datetime
from typing import Dict, Optional, Type, Union

from pydantic import BaseModel, Field


class VpcLatticeV2RequestContextIdentity(BaseModel):
    source_vpc_arn: Optional[str] = Field(None, alias="sourceVpcArn")
    get_type: Optional[str] = Field(None, alias="type")
    principal: Optional[str] = Field(None, alias="principal")
    principal_org_id: Optional[str] = Field(None, alias="principalOrgID")
    session_name: Optional[str] = Field(None, alias="sessionName")
    x509_subject_cn: Optional[str] = Field(None, alias="X509SubjectCn")
    x509_issuer_ou: Optional[str] = Field(None, alias="X509IssuerOu")
    x509_san_dns: Optional[str] = Field(None, alias="x509SanDns")
    x509_san_uri: Optional[str] = Field(None, alias="X509SanUri")
    x509_san_name_cn: Optional[str] = Field(None, alias="X509SanNameCn")


class VpcLatticeV2RequestContext(BaseModel):
    service_network_arn: str = Field(alias="serviceNetworkArn")
    service_arn: str = Field(alias="serviceArn")
    target_group_arn: str = Field(alias="targetGroupArn")
    identity: VpcLatticeV2RequestContextIdentity
    region: str
    time_epoch: datetime = Field(alias="timeEpoch")


class VpcLatticeV2Model(BaseModel):
    version: str
    path: str
    method: str
    headers: Dict[str, str]
    query_string_parameters: Optional[Dict[str, str]] = None
    body: Optional[Union[str, Type[BaseModel]]] = None
    is_base64_encoded: Optional[bool] = Field(None, alias="isBase64Encoded")
    request_context: VpcLatticeV2RequestContext = Field(None, alias="requestContext")
