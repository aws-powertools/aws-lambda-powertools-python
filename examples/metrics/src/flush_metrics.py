from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

metrics = Metrics()


def lambda_handler(event: dict, context: LambdaContext):
    try:
        metrics.add_metric(name="SuccessfulBooking", unit=MetricUnit.Count, value=1)
    finally:
        metrics.flush_metrics()
