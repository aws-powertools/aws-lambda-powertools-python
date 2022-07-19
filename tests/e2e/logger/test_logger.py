import boto3
import pytest
from e2e import conftest
from e2e.utils import helpers


@pytest.fixture(scope="module")
def config() -> conftest.LambdaConfig:
    return {
        "parameters": {},
        "environment_variables": {
            "MESSAGE": "logger message test",
            "LOG_LEVEL": "INFO",
            "ADDITIONAL_KEY": "extra_info",
        },
    }


def test_basic_lambda_logs_visible(execute_lambda: conftest.InfrastructureOutput, config: conftest.LambdaConfig):
    # GIVEN
    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="basichandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert any(
        log.message == config["environment_variables"]["MESSAGE"]
        and log.level == config["environment_variables"]["LOG_LEVEL"]
        for log in filtered_logs
    )


def test_basic_lambda_no_debug_logs_visible(
    execute_lambda: conftest.InfrastructureOutput, config: conftest.LambdaConfig
):
    # GIVEN
    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="basichandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert not any(
        log.message == config["environment_variables"]["MESSAGE"] and log.level == "DEBUG" for log in filtered_logs
    )


def test_basic_lambda_contextual_data_logged(execute_lambda: conftest.InfrastructureOutput):
    # GIVEN
    required_keys = (
        "xray_trace_id",
        "function_request_id",
        "function_arn",
        "function_memory_size",
        "function_name",
        "cold_start",
    )

    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="basichandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert all(keys in logs.dict(exclude_unset=True) for logs in filtered_logs for keys in required_keys)


def test_basic_lambda_additional_key_persistence_basic_lambda(
    execute_lambda: conftest.InfrastructureOutput, config: conftest.LambdaConfig
):
    # GIVEN
    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="basichandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert any(
        log.extra_info
        and log.message == config["environment_variables"]["MESSAGE"]
        and log.level == config["environment_variables"]["LOG_LEVEL"]
        for log in filtered_logs
    )


def test_basic_lambda_empty_event_logged(execute_lambda: conftest.InfrastructureOutput):

    # GIVEN
    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="basichandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert any(log.message == {} for log in filtered_logs)


def test_no_context_lambda_contextual_data_not_logged(execute_lambda: conftest.InfrastructureOutput):

    # GIVEN
    required_missing_keys = (
        "function_request_id",
        "function_arn",
        "function_memory_size",
        "function_name",
        "cold_start",
    )

    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="nocontexthandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert not any(keys in logs.dict(exclude_unset=True) for logs in filtered_logs for keys in required_missing_keys)


def test_no_context_lambda_event_not_logged(execute_lambda: conftest.InfrastructureOutput):

    # GIVEN
    lambda_name = execute_lambda.get_lambda_function_name(cf_output_name="nocontexthandlerarn")
    timestamp = execute_lambda.get_lambda_execution_time_timestamp()
    cw_client = boto3.client("logs")

    # WHEN
    filtered_logs = helpers.get_logs(lambda_function_name=lambda_name, start_time=timestamp, log_client=cw_client)

    # THEN
    assert not any(log.message == {} for log in filtered_logs)
