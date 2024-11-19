from typing import Optional

from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from tests.functional.utils import load_event


def test_exception_handler_with_single_resolver():
    # GIVEN a AppSyncResolver instance
    mock_event = load_event("appSyncDirectResolver.json")

    app = AppSyncResolver()

    # WHEN we configure exception handler for ValueError
    @app.exception_handler(ValueError)
    def handle_value_error(ex: ValueError):
        return {"message": "error"}

    @app.resolver(field_name="createSomething")
    def create_something(id: str):  # noqa AA03 VNE003
        raise ValueError("Error")

    # Call the implicit handler
    result = app(mock_event, {})

    # THEN the return must be the Exception Handler error message
    assert result["message"] == "error"


def test_exception_handler_with_batch_resolver_and_raise_exception():

    # GIVEN a AppSyncResolver instance
    app = AppSyncResolver()

    event = [
        {
            "typeName": "Query",
            "info": {
                "fieldName": "listLocations",
                "parentTypeName": "Post",
            },
            "fieldName": "listLocations",
            "arguments": {},
            "source": {
                "id": "1",
            },
        },
        {
            "typeName": "Query",
            "info": {
                "fieldName": "listLocations",
                "parentTypeName": "Post",
            },
            "fieldName": "listLocations",
            "arguments": {},
            "source": {
                "id": "2",
            },
        },
        {
            "typeName": "Query",
            "info": {
                "fieldName": "listLocations",
                "parentTypeName": "Post",
            },
            "fieldName": "listLocations",
            "arguments": {},
            "source": {
                "id": [3, 4],
            },
        },
    ]

    # WHEN we configure exception handler for ValueError
    @app.exception_handler(ValueError)
    def handle_value_error(ex: ValueError):
        return {"message": "error"}

    # WHEN the sync batch resolver for the 'listLocations' field is defined with raise_on_error=True
    @app.batch_resolver(field_name="listLocations", raise_on_error=True, aggregate=False)
    def create_something(event: AppSyncResolverEvent) -> Optional[list]:  # noqa AA03 VNE003
        raise ValueError

    # Call the implicit handler
    result = app(event, {})

    # THEN the return must be the Exception Handler error message
    assert result["message"] == "error"


def test_exception_handler_with_batch_resolver_and_no_raise_exception():

    # GIVEN a AppSyncResolver instance
    app = AppSyncResolver()

    event = [
        {
            "typeName": "Query",
            "info": {
                "fieldName": "listLocations",
                "parentTypeName": "Post",
            },
            "fieldName": "listLocations",
            "arguments": {},
            "source": {
                "id": "1",
            },
        },
        {
            "typeName": "Query",
            "info": {
                "fieldName": "listLocations",
                "parentTypeName": "Post",
            },
            "fieldName": "listLocations",
            "arguments": {},
            "source": {
                "id": "2",
            },
        },
        {
            "typeName": "Query",
            "info": {
                "fieldName": "listLocations",
                "parentTypeName": "Post",
            },
            "fieldName": "listLocations",
            "arguments": {},
            "source": {
                "id": [3, 4],
            },
        },
    ]

    # WHEN we configure exception handler for ValueError
    @app.exception_handler(ValueError)
    def handle_value_error(ex: ValueError):
        return {"message": "error"}

    # WHEN the sync batch resolver for the 'listLocations' field is defined with raise_on_error=False
    @app.batch_resolver(field_name="listLocations", raise_on_error=False, aggregate=False)
    def create_something(event: AppSyncResolverEvent) -> Optional[list]:  # noqa AA03 VNE003
        raise ValueError

    # Call the implicit handler
    result = app(event, {})

    # THEN the return must not trigger the Exception Handler, but instead return from the resolver
    assert result == [None, None, None]
