import json
import os
import warnings
from collections import namedtuple

import pytest
from test_metrics_provider import capture_metrics_output

from aws_lambda_powertools.metrics.exceptions import MetricValueError, SchemaValidationError
from aws_lambda_powertools.metrics.provider.cold_start import reset_cold_start_flag
from aws_lambda_powertools.metrics.provider.datadog import DatadogMetrics, DatadogProvider


def test_datadog_coldstart(capsys, namespace):
    reset_cold_start_flag()
    dd_provider = DatadogProvider(namespace=namespace, flush_to_log=True)
    metrics = DatadogMetrics(provider=dd_provider)

    LambdaContext = namedtuple("LambdaContext", "function_name")

    @metrics.log_metrics(capture_cold_start_metric=True, raise_on_empty_metrics=True)
    def lambda_handler(event, context):
        metrics.add_metric(name="item_sold", value=1, tags=["product:latte", "order:online"])

    lambda_handler({}, LambdaContext("example_fn2"))
    logs = capsys.readouterr().out.strip()
    assert "ColdStart" in logs


def test_datadog_write_to_log_with_env_variable(capsys, namespace):
    os.environ["DD_FLUSH_TO_LOG"] = "True"
    dd_provider = DatadogProvider(namespace=namespace)
    metrics = DatadogMetrics(provider=dd_provider)
    metrics.add_metric(name="item_sold", value=1, tags=["product:latte", "order:online"])
    metrics.flush_metrics()
    logs = capture_metrics_output(capsys)
    logs["e"] = ""
    assert logs == json.loads('{"m":"test_namespace.item_sold","v":1,"e":"","t":["product:latte","order:online"]}')


def test_datadog_with_invalid_value(capsys, namespace):
    dd_provider = DatadogProvider(namespace=namespace)
    metrics = DatadogMetrics(provider=dd_provider)

    with pytest.raises(MetricValueError, match=".*is not a valid number"):
        metrics.add_metric(name="item_sold", value="a", tags=["product:latte", "order:online"])


def test_datadog_with_namespace(capsys, namespace):
    metrics = DatadogMetrics(namespace=namespace, flush_to_log=True)

    LambdaContext = namedtuple("LambdaContext", "function_name")

    @metrics.log_metrics(capture_cold_start_metric=True, raise_on_empty_metrics=True)
    def lambda_handler(event, context):
        metrics.add_metric(name="item_sold", value=1, tags=["product:latte", "order:online"])

    lambda_handler({}, LambdaContext("example_fn"))
    logs = capsys.readouterr().out.strip()
    assert namespace in logs


def test_datadog_raise_on_empty(namespace):
    dd_provider = DatadogProvider(namespace=namespace, flush_to_log=True)
    metrics = DatadogMetrics(provider=dd_provider)

    LambdaContext = namedtuple("LambdaContext", "function_name")

    @metrics.log_metrics(capture_cold_start_metric=False, raise_on_empty_metrics=True)
    def lambda_handler(event, context):
        pass

    with pytest.raises(SchemaValidationError, match="Must contain at least one metric."):
        lambda_handler({}, LambdaContext("example_fn"))


def test_datadog_args(capsys, namespace):
    dd_provider = DatadogProvider(namespace=namespace, flush_to_log=True)
    metrics = DatadogMetrics(provider=dd_provider)
    metrics.add_metric("order_valve", 12.45, sales="sam")
    metrics.flush_metrics()
    logs = capsys.readouterr().out.strip()
    log_dict = json.loads(logs)
    tag_list = log_dict.get("t")
    assert "sales:sam" in tag_list


def test_datadog_kwargs(capsys, namespace):
    dd_provider = DatadogProvider(namespace=namespace, flush_to_log=True)
    metrics = DatadogMetrics(provider=dd_provider)
    metrics.add_metric(
        name="order_valve",
        value=12.45,
        tags=["test:kwargs"],
        str="str",
        int=123,
        float=45.6,
        dict={"type": "termination identified"},
    )
    metrics.flush_metrics()
    logs = capsys.readouterr().out.strip()
    log_dict = json.loads(logs)
    tag_list = log_dict.get("t")
    assert "test:kwargs" in tag_list
    assert "str:str" in tag_list
    assert "int:123" in tag_list
    assert "float:45.6" in tag_list


def test_log_metrics_clear_metrics_after_invocation(metric, service, namespace):
    # GIVEN Metrics is initialized
    my_metrics = DatadogMetrics(namespace=namespace, flush_to_log=True)
    my_metrics.add_metric(**metric)

    # WHEN log_metrics is used to flush metrics from memory
    @my_metrics.log_metrics
    def lambda_handler(evt, context):
        pass

    lambda_handler({}, {})

    # THEN metric set should be empty after function has been run
    assert my_metrics.metric_set == []


def test_log_metrics_decorator_no_metrics_warning(dimensions, namespace, service):
    # GIVEN Metrics is initialized
    my_metrics = DatadogMetrics(namespace=namespace, flush_to_log=True)

    # WHEN using the log_metrics decorator and no metrics have been added
    @my_metrics.log_metrics
    def lambda_handler(evt, context):
        pass

    # THEN it should raise a warning instead of throwing an exception
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("default")
        lambda_handler({}, {})
        assert len(w) == 1
        assert str(w[-1].message) == (
            "No application metrics to publish. The cold-start metric may be published if enabled. "
            "If application metrics should never be empty, consider using 'raise_on_empty_metrics'"
        )


def test_log_metrics_with_default_namespace(metric, capsys, namespace):
    # GIVEN Metrics is initialized
    dd_provider = DatadogProvider(flush_to_log=True)
    metrics = DatadogMetrics(provider=dd_provider)

    LambdaContext = namedtuple("LambdaContext", "function_name")

    @metrics.log_metrics(capture_cold_start_metric=True, raise_on_empty_metrics=True)
    def lambda_handler(event, context):
        metrics.add_metric(name="item_sold", value=1, tags=["product:latte", "order:online"])

    lambda_handler({}, LambdaContext("example_fn2"))
    logs = capsys.readouterr().out.strip()
    assert namespace not in logs
