import json

from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, IdempotencyConfig, idempotent

persistence_layer = DynamoDBPersistenceLayer(table_name="IdempotencyTable")

# Treat everything under the "body" key
# in the event json object as our payload
config = IdempotencyConfig(event_key_jmespath="powertools_json(body)")


@idempotent(config=config, persistence_store=persistence_layer)
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    payment = create_subscription_payment(user=body["user"], product_id=body["product_id"])
    ...
    return {"payment_id": payment.id, "message": "success", "statusCode": 200}


def create_subscription_payment(user: str, product_id: str) -> dict:
    return {"id": "1", "message": "paid"}
