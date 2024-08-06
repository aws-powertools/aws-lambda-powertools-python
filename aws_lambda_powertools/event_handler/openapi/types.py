import types
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Set, Type, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from pydantic import BaseModel  # noqa: F401

CacheKey = Optional[Callable[..., Any]]
IncEx = Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any]]
ModelNameMap = Dict[Union[Type["BaseModel"], Type[Enum]], str]
TypeModelOrEnum = Union[Type["BaseModel"], Type[Enum]]
UnionType = getattr(types, "UnionType", Union)


COMPONENT_REF_PREFIX = "#/components/schemas/"
COMPONENT_REF_TEMPLATE = "#/components/schemas/{model}"
METHODS_WITH_BODY = {"GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"}


validation_error_definition = {
    "title": "ValidationError",
    "type": "object",
    "properties": {
        "loc": {
            "title": "Location",
            "type": "array",
            "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
        },
        # For security reasons, we hide **msg** details (don't leak Python, Pydantic or filenames)
        "type": {"title": "Error Type", "type": "string"},
    },
    "required": ["loc", "msg", "type"],
}

validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "detail": {
            "title": "Detail",
            "type": "array",
            "items": {"$ref": f"{COMPONENT_REF_PREFIX}ValidationError"},
        },
    },
}


class OpenAPIResponseContentSchema(TypedDict, total=False):
    schema: Dict


class OpenAPIResponseContentModel(TypedDict):
    model: Any


class OpenAPIResponse(TypedDict):
    description: str
    content: NotRequired[Dict[str, Union[OpenAPIResponseContentSchema, OpenAPIResponseContentModel]]]
