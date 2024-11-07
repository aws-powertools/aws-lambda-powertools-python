from typing import Any, Type

from pydantic import BaseModel, Json

from aws_lambda_powertools.utilities.parser import BaseEnvelope, event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext


class CancelOrder(BaseModel):
    order_id: int
    reason: str


class CancelOrderModel(BaseModel):
    body: Json[CancelOrder]


class CustomEnvelope(BaseEnvelope):
    def parse(self, data: dict, model: Type[BaseModel]) -> Any:
        return model.model_validate({"body": data.get("body", {})})


@event_parser(model=CancelOrderModel, envelope=CustomEnvelope)
def lambda_handler(event: CancelOrderModel, context: LambdaContext):
    cancel_order: CancelOrder = event.body

    assert cancel_order.order_id is not None

    # Process the cancel order request
    print(f"Cancelling order {cancel_order.order_id} for reason: {cancel_order.reason}")

    return {
        "statusCode": 200,
        "body": f"Order {cancel_order.order_id} cancelled successfully",
    }
