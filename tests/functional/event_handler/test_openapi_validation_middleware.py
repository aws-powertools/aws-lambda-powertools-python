import json
from typing import Annotated

from pydantic import BaseModel

from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.event_handler.openapi.params import Body
from tests.functional.utils import load_event

LOAD_GW_EVENT = load_event("apiGatewayProxyEvent.json")


def test_validate_scalars():
    app = ApiGatewayResolver(enable_validation=True)

    @app.get("/users/<user_id>")
    def handler(user_id: int):
        print(user_id)

    # sending a number
    LOAD_GW_EVENT["path"] = "/users/123"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200

    # sending a string
    LOAD_GW_EVENT["path"] = "/users/abc"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 422
    assert "Input should be a valid integer, unable to parse string as an integer" in result["body"]


def test_validate_scalars_with_default():
    app = ApiGatewayResolver(enable_validation=True)

    @app.get("/users/<user_id>")
    def handler(user_id: int = 123):
        print(user_id)

    # sending a number
    LOAD_GW_EVENT["path"] = "/users/123"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200

    # sending a string
    LOAD_GW_EVENT["path"] = "/users/abc"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 422
    assert "Input should be a valid integer, unable to parse string as an integer" in result["body"]


def test_validate_scalars_with_default_and_optional():
    app = ApiGatewayResolver(enable_validation=True)

    @app.get("/users/<user_id>")
    def handler(user_id: int = 123, include_extra: bool = False):
        print(user_id)

    # sending a number
    LOAD_GW_EVENT["path"] = "/users/123"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200

    # sending a string
    LOAD_GW_EVENT["path"] = "/users/abc"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 422
    assert "Input should be a valid integer, unable to parse string as an integer" in result["body"]


def test_validate_return_type():
    app = ApiGatewayResolver(enable_validation=True)

    @app.get("/")
    def handler() -> int:
        return 123

    LOAD_GW_EVENT["path"] = "/"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200
    assert result["body"] == 123


def test_validate_return_model():
    app = ApiGatewayResolver(enable_validation=True)

    class Model(BaseModel):
        name: str
        age: int

    @app.get("/")
    def handler() -> Model:
        return Model(name="John", age=30)

    LOAD_GW_EVENT["path"] = "/"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200
    assert result["body"] == {"name": "John", "age": 30}


def test_validate_invalid_return_model():
    app = ApiGatewayResolver(enable_validation=True)

    class Model(BaseModel):
        name: str
        age: int

    @app.get("/")
    def handler() -> Model:
        return {"name": "John"}  # type: ignore

    LOAD_GW_EVENT["path"] = "/"

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 422
    assert "Field required" in result["body"]


def test_validate_body_param():
    app = ApiGatewayResolver(enable_validation=True)

    class Model(BaseModel):
        name: str
        age: int

    @app.post("/")
    def handler(user: Model) -> Model:
        return user

    LOAD_GW_EVENT["httpMethod"] = "POST"
    LOAD_GW_EVENT["path"] = "/"
    LOAD_GW_EVENT["body"] = json.dumps({"name": "John", "age": 30})

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200
    assert result["body"] == {"name": "John", "age": 30}


def test_validate_embed_body_param():
    app = ApiGatewayResolver(enable_validation=True)

    class Model(BaseModel):
        name: str
        age: int

    @app.post("/")
    def handler(user: Annotated[Model, Body(embed=True)]) -> Model:
        return user

    LOAD_GW_EVENT["httpMethod"] = "POST"
    LOAD_GW_EVENT["path"] = "/"
    LOAD_GW_EVENT["body"] = json.dumps({"name": "John", "age": 30})

    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 422
    assert "Field required" in result["body"]

    LOAD_GW_EVENT["body"] = json.dumps({"user": {"name": "John", "age": 30}})
    result = app(LOAD_GW_EVENT, {})
    assert result["statusCode"] == 200
