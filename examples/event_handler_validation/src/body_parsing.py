from typing import Optional

import requests
from pydantic import BaseModel, Field

from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayHttpResolver(enable_validation=True)


class Todo(BaseModel):
    userId: int
    id_: Optional[int] = Field(alias="id", default=None)
    title: str
    completed: bool


@app.post("/todos")
def create_todo(todo: Todo) -> int:
    response = requests.post("https://jsonplaceholder.typicode.com/todos", json=todo.dict(by_alias=True))
    response.raise_for_status()

    return response.json()["id"]


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
