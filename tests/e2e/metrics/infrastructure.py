from tests.e2e.utils.infrastructure import BaseInfrastructure


class MetricsStack(BaseInfrastructure):
    FEATURE_NAME = "metrics"

    def __init__(self, feature_name: str = FEATURE_NAME) -> None:
        super().__init__(feature_name)

    def create_resources(self):
        self.create_lambda_functions()
