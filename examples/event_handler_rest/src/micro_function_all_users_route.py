import json
from http import HTTPStatus

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()

# This would likely be a db lookup
users = [
    {
        "user_id": "b0b2a5bf-ee1e-4c5e-9a86-91074052739e",
        "email": "john.doe@example.com",
        "active": True,
    },
    {
        "user_id": "3a9df6b1-938c-4e80-bd4a-0c966f4b1c1e",
        "email": "jane.smith@example.com",
        "active": True,
    },
    {
        "user_id": "aa0d3d09-9cb9-42b9-9e63-1fb17ea52981",
        "email": "alex.wilson@example.com",
        "active": True,
    },
    {
        "user_id": "67a6c17d-b7f0-4f79-aae0-79f4a53c113b",
        "email": "lisa.johnson@example.com",
        "active": True,
    },
    {
        "user_id": "6e85cf66-47af-4dbf-8aa2-2db3c24f29c1",
        "email": "michael.brown@example.com",
        "active": False,
    },
]


class User(BaseModel):
    user_id: str
    email: str
    active: bool


app = APIGatewayRestResolver()


@app.get("/users")
def all_active_users():
    """HTTP Response for all active users"""
    all_users = [User(**user) for user in users]
    all_active_users = [user.dict() for user in all_users if user.active]

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type="application/json",
        body=json.dumps(all_active_users),
    )


@logger.inject_lambda_context()
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
