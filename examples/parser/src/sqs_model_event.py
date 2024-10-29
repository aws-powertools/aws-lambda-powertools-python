from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.parser.models import SqsModel
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: dict, context: LambdaContext) -> None:
    parsed_event = parse(model=SqsModel, event=event)

    results = []
    for record in parsed_event.Records:
        results.append({
            'Message ID':record.messageId, 
            'body':record.body
            })
    return results