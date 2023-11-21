from typing import List

import requests
from pydantic import BaseModel, EmailStr, Field

from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayHttpResolver(enable_validation=True)


class Todo(BaseModel):
    userId: int
    id_: int = Field(alias="id")
    title: str
    completed: bool


@app.get("/todos")
def get_todos_by_email(email: EmailStr) -> List[Todo]:
    todos = requests.get(f"https://jsonplaceholder.typicode.com/todos?email={email}")
    todos.raise_for_status()

    return todos.json()


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


if __name__ == "__main__":
    print(app.get_openapi_schema().dict())
