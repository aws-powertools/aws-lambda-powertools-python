import base64
import json
import re
import zlib
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from aws_lambda_powertools.shared.json_encoder import Encoder
from aws_lambda_powertools.utilities.data_classes import ALBEvent, APIGatewayProxyEvent, APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.data_classes.common import BaseProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext


class ProxyEventType(Enum):
    """An enumerations of the supported proxy event types.

    **NOTE:** api_gateway is an alias of http_api_v1"""

    http_api_v1 = "APIGatewayProxyEvent"
    http_api_v2 = "APIGatewayProxyEventV2"
    alb_event = "ALBEvent"
    api_gateway = http_api_v1


class CORSConfig(object):
    """CORS Config


    Examples
    --------

    Simple cors example using the default permissive cors, not this should only be used during early prototyping

        >>> from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver
        >>>
        >>> app = ApiGatewayResolver()
        >>>
        >>> @app.get("/my/path", cors=True)
        >>> def with_cors():
        >>>      return {"message": "Foo"}

    Using a custom CORSConfig where `with_cors` used the custom provided CORSConfig and `without_cors`
    do not include any cors headers.

        >>> from aws_lambda_powertools.event_handler.api_gateway import (
        >>>    ApiGatewayResolver, CORSConfig
        >>> )
        >>>
        >>> cors_config = CORSConfig(
        >>>    allow_origin="https://wwww.example.com/",
        >>>    expose_headers=["x-exposed-response-header"],
        >>>    allow_headers=["x-custom-request-header"],
        >>>    max_age=100,
        >>>    allow_credentials=True,
        >>> )
        >>> app = ApiGatewayResolver(cors=cors_config)
        >>>
        >>> @app.get("/my/path", cors=True)
        >>> def with_cors():
        >>>      return {"message": "Foo"}
        >>>
        >>> @app.get("/another-one")
        >>> def without_cors():
        >>>     return {"message": "Foo"}
    """

    _REQUIRED_HEADERS = ["Authorization", "Content-Type", "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token"]

    def __init__(
        self,
        allow_origin: str = "*",
        allow_headers: List[str] = None,
        expose_headers: List[str] = None,
        max_age: int = None,
        allow_credentials: bool = False,
    ):
        """
        Parameters
        ----------
        allow_origin: str
            The value of the `Access-Control-Allow-Origin` to send in the response. Defaults to "*", but should
            only be used during development.
        allow_headers: str
            The list of additional allowed headers. This list is added to list of
            built in allowed headers: `Authorization`, `Content-Type`, `X-Amz-Date`,
            `X-Api-Key`, `X-Amz-Security-Token`.
        expose_headers: str
            A list of values to return for the Access-Control-Expose-Headers
        max_age: int
            The value for the `Access-Control-Max-Age`
        allow_credentials: bool
            A boolean value that sets the value of `Access-Control-Allow-Credentials`
        """
        self.allow_origin = allow_origin
        self.allow_headers = set(self._REQUIRED_HEADERS + (allow_headers or []))
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        self.allow_credentials = allow_credentials

    def to_dict(self) -> Dict[str, str]:
        """Builds the configured Access-Control http headers"""
        headers = {
            "Access-Control-Allow-Origin": self.allow_origin,
            "Access-Control-Allow-Headers": ",".join(sorted(self.allow_headers)),
        }
        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = ",".join(self.expose_headers)
        if self.max_age is not None:
            headers["Access-Control-Max-Age"] = str(self.max_age)
        if self.allow_credentials is True:
            headers["Access-Control-Allow-Credentials"] = "true"
        return headers


class Response:
    """Response data class that provides greater control over what is returned from the proxy event"""

    def __init__(
        self, status_code: int, content_type: Optional[str], body: Union[str, bytes, None], headers: Dict = None
    ):
        """

        Parameters
        ----------
        status_code: int
            Http status code, example 200
        content_type: str
            Optionally set the Content-Type header, example "application/json". Note this will be merged into any
            provided http headers
        body: Union[str, bytes, None]
            Optionally set the response body. Note: bytes body will be automatically base64 encoded
        headers: dict
            Optionally set specific http headers. Setting "Content-Type" hear would override the `content_type` value.
        """
        self.status_code = status_code
        self.body = body
        self.base64_encoded = False
        self.headers: Dict = headers or {}
        if content_type:
            self.headers.setdefault("Content-Type", content_type)


class Route:
    """Internally used Route Configuration"""

    def __init__(
        self, method: str, rule: Any, func: Callable, cors: bool, compress: bool, cache_control: Optional[str]
    ):
        self.method = method.upper()
        self.rule = rule
        self.func = func
        self.cors = cors
        self.compress = compress
        self.cache_control = cache_control


class ResponseBuilder:
    """Internally used Response builder"""

    def __init__(self, response: Response, route: Route = None):
        self.response = response
        self.route = route

    def _add_cors(self, cors: CORSConfig):
        """Update headers to include the configured Access-Control headers"""
        self.response.headers.update(cors.to_dict())

    def _add_cache_control(self, cache_control: str):
        """Set the specified cache control headers for 200 http responses. For non-200 `no-cache` is used."""
        self.response.headers["Cache-Control"] = cache_control if self.response.status_code == 200 else "no-cache"

    def _compress(self):
        """Compress the response body, but only if `Accept-Encoding` headers includes gzip."""
        self.response.headers["Content-Encoding"] = "gzip"
        if isinstance(self.response.body, str):
            self.response.body = bytes(self.response.body, "utf-8")
        gzip = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        self.response.body = gzip.compress(self.response.body) + gzip.flush()

    def _route(self, event: BaseProxyEvent, cors: Optional[CORSConfig]):
        """Optionally handle any of the route's configure response handling"""
        if self.route is None:
            return
        if self.route.cors:
            self._add_cors(cors or CORSConfig())
        if self.route.cache_control:
            self._add_cache_control(self.route.cache_control)
        if self.route.compress and "gzip" in (event.get_header_value("accept-encoding", "") or ""):
            self._compress()

    def build(self, event: BaseProxyEvent, cors: CORSConfig = None) -> Dict[str, Any]:
        """Build the full response dict to be returned by the lambda"""
        self._route(event, cors)

        if isinstance(self.response.body, bytes):
            self.response.base64_encoded = True
            self.response.body = base64.b64encode(self.response.body).decode()
        return {
            "statusCode": self.response.status_code,
            "headers": self.response.headers,
            "body": self.response.body,
            "isBase64Encoded": self.response.base64_encoded,
        }


class ApiGatewayResolver:
    """API Gateway and ALB proxy resolver

    Examples
    --------
    Simple example with a custom lambda handler using the Tracer capture_lambda_handler decorator

        >>> from aws_lambda_powertools import Tracer
        >>> from aws_lambda_powertools.event_handler.api_gateway import (
        >>>    ApiGatewayResolver
        >>> )
        >>>
        >>> tracer = Tracer()
        >>> app = ApiGatewayResolver()
        >>>
        >>> @app.get("/get-call")
        >>> def simple_get():
        >>>      return {"message": "Foo"}
        >>>
        >>> @app.post("/post-call")
        >>> def simple_post():
        >>>     post_data: dict = app.current_event.json_body
        >>>     return {"message": post_data["value"]}
        >>>
        >>> @tracer.capture_lambda_handler
        >>> def lambda_handler(event, context):
        >>>    return app.resolve(event, context)

    """

    current_event: BaseProxyEvent
    lambda_context: LambdaContext

    def __init__(self, proxy_type: Enum = ProxyEventType.http_api_v1, cors: CORSConfig = None):
        """
        Parameters
        ----------
        proxy_type: ProxyEventType
            Proxy request type, defaults to API Gateway V1
        cors: CORSConfig
            Optionally configure and enabled CORS. Not each route will need to have to cors=True
        """
        self._proxy_type = proxy_type
        self._routes: List[Route] = []
        self._cors = cors
        self._cors_methods: Set[str] = {"OPTIONS"}

    def get(self, rule: str, cors: bool = False, compress: bool = False, cache_control: str = None):
        """Get route decorator with GET `method`"""
        return self.route(rule, "GET", cors, compress, cache_control)

    def post(self, rule: str, cors: bool = False, compress: bool = False, cache_control: str = None):
        """Post route decorator with POST `method`"""
        return self.route(rule, "POST", cors, compress, cache_control)

    def put(self, rule: str, cors: bool = False, compress: bool = False, cache_control: str = None):
        """Put route decorator with PUT `method`"""
        return self.route(rule, "PUT", cors, compress, cache_control)

    def delete(self, rule: str, cors: bool = False, compress: bool = False, cache_control: str = None):
        """Delete route decorator with DELETE `method`"""
        return self.route(rule, "DELETE", cors, compress, cache_control)

    def patch(self, rule: str, cors: bool = False, compress: bool = False, cache_control: str = None):
        """Patch route decorator with PATCH `method`"""
        return self.route(rule, "PATCH", cors, compress, cache_control)

    def route(self, rule: str, method: str, cors: bool = False, compress: bool = False, cache_control: str = None):
        """Route decorator includes parameter `method`"""

        def register_resolver(func: Callable):
            self._routes.append(Route(method, self._compile_regex(rule), func, cors, compress, cache_control))
            if cors:
                self._cors_methods.add(method.upper())
            return func

        return register_resolver

    def resolve(self, event, context) -> Dict[str, Any]:
        """Resolves the response based on the provide event and decorator routes

        Parameters
        ----------
        event: Dict[str, Any]
            Event
        context: LambdaContext
            Lambda context
        Returns
        -------
        dict
            Returns the dict response
        """
        self.current_event = self._to_proxy_event(event)
        self.lambda_context = context
        return self._resolve().build(self.current_event, self._cors)

    def __call__(self, event, context) -> Any:
        return self.resolve(event, context)

    @staticmethod
    def _compile_regex(rule: str):
        """Precompile regex pattern"""
        rule_regex: str = re.sub(r"(<\w+>)", r"(?P\1.+)", rule)
        return re.compile("^{}$".format(rule_regex))

    def _to_proxy_event(self, event: Dict) -> BaseProxyEvent:
        """Convert the event dict to the corresponding data class"""
        if self._proxy_type == ProxyEventType.http_api_v1:
            return APIGatewayProxyEvent(event)
        if self._proxy_type == ProxyEventType.http_api_v2:
            return APIGatewayProxyEventV2(event)
        return ALBEvent(event)

    def _resolve(self) -> ResponseBuilder:
        """Resolves the response or return the not found response"""
        method = self.current_event.http_method.upper()
        path = self.current_event.path
        for route in self._routes:
            if method != route.method:
                continue
            match: Optional[re.Match] = route.rule.match(path)
            if match:
                return self._call_route(route, match.groupdict())

        return self._not_found(method, path)

    def _not_found(self, method: str, path: str) -> ResponseBuilder:
        """Called when no matching route was found and includes support for the cors preflight response"""
        headers = {}
        if self._cors:
            headers.update(self._cors.to_dict())

            if method == "OPTIONS":  # Preflight
                headers["Access-Control-Allow-Methods"] = ",".join(sorted(self._cors_methods))
                return ResponseBuilder(Response(status_code=204, content_type=None, headers=headers, body=None))

        return ResponseBuilder(
            Response(
                status_code=404,
                content_type="application/json",
                headers=headers,
                body=json.dumps({"message": f"No route found for '{method}.{path}'"}),
            )
        )

    def _call_route(self, route: Route, args: Dict[str, str]) -> ResponseBuilder:
        """Actually call the matching route with any provided keyword arguments."""
        return ResponseBuilder(self._to_response(route.func(**args)), route)

    @staticmethod
    def _to_response(result: Union[Tuple[int, str, Union[bytes, str]], Dict, Response]) -> Response:
        """Convert the route's result to a Response

         3 main result types are supported:

        - Tuple[int, str, bytes] and Tuple[int, str, str]: status code, content-type and body (str|bytes)
        - Dict[str, Any]: Rest api response with just the Dict to json stringify and content-type is set to
          application/json
        - Response: returned as is, and allows for more flexibility
        """
        if isinstance(result, Response):
            return result
        elif isinstance(result, dict):
            return Response(
                status_code=200,
                content_type="application/json",
                body=json.dumps(result, separators=(",", ":"), cls=Encoder),
            )
        else:  # Tuple[int, str, Union[bytes, str]]
            return Response(*result)
