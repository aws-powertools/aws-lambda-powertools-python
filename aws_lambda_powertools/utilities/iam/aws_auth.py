
from typing import Optional
from enum import Enum
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
import botocore.session


class AWSServicePrefix(Enum):
    LATTICE = "vpc-lattice-svcs"
    RESTAPI = "execute-api"
    HTTPAPI = "apigateway"
    APPSYNC = "appsync"


class AWSSigV4Auth:
    """
    Authenticating Requests (AWS Signature Version 4)

    Args:
        region (str): AWS region
        service (str): AWS service
        access_key (str, optional): AWS access key
        secret_key (str, optional): AWS secret key
        token (str, optional): AWS session token

    Returns:
        SigV4Auth: SigV4Auth instance

    Examples
    --------
    **Using default credentials**
    >>> from aws_lambda_powertools.utilities.iam import SigV4AuthFactory
    >>> auth = SigV4AuthFactory(region="us-east-2", service="vpc-lattice-svcs")
    """


    def __init__(
        self,
        url: str,
        region: Optional[str],
        body: Optional[str] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        method: Optional[str] = "GET",
        service: Enum = AWSServicePrefix.LATTICE,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        token: Optional[str] = None,
    ):

        self.service = service.value
        self.region = region
        self.method = method
        self.url = url
        self.data = body
        self.params = params
        self.headers = headers

        if access_key and secret_key and token:
            self.access_key = access_key
            self.secret_key = secret_key
            self.token = token
            self.credentials = Credentials(access_key=self.access_key, secret_key=self.secret_key, token=self.token)
        else:
            credentials = botocore.session.Session().get_credentials()
            self.credentials = credentials.get_frozen_credentials()

        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}

        sigv4 = SigV4Auth(credentials=self.credentials, service_name=self.service, region_name=self.region)

        request = AWSRequest(method=self.method, url=self.url, data=self.data, params=self.params, headers=self.headers)

        if self.service == AWSServicePrefix.LATTICE.value:
            # payload signing is not supported for vpc-lattice-svcs
            request.context["payload_signing_enabled"] = False

        sigv4.add_auth(request)
        self.signed_request = request.prepare()

        def __call__(self):
            return self.signed_request
