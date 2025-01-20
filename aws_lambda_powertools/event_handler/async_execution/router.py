from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from .routes.aws_config_rule import AwsConfigRuleRoute
from .routes.cloud_watch_alarm import CloudWatchAlarmRoute
from .routes.cloud_watch_logs import CloudWatchLogsRoute
from .routes.code_deploy_lifecycle_hook import CodeDeployLifecycleHookRoute
from .routes.event_bridge import EventBridgeRoute
from .routes.s3 import S3Route
from .routes.secrets_manager import SecretsManagerRoute
from .routes.ses import SESRoute
from .routes.sns import SNSRoute

if TYPE_CHECKING:
    from .routes.base import BaseRoute


class Router:
    _routes: list[BaseRoute]

    def __init__(self):
        self._routes = []

    def aws_config_rule(
        self,
        arn: str | None = None,
        rule_name: str | None = None,
        rule_name_prefix: str | None = None,
        rule_id: str | None = None,
    ) -> Callable:
        def wrapper_aws_config_rule(func: Callable):
            self._routes.append(
                AwsConfigRuleRoute(
                    func=func,
                    arn=arn,
                    rule_name=rule_name,
                    rule_name_prefix=rule_name_prefix,
                    rule_id=rule_id,
                ),
            )

        return wrapper_aws_config_rule

    def cloud_watch_alarm(
        self,
        arn: str | None = None,
        alarm_name: str | None = None,
        alarm_name_prefix: str | None = None,
    ) -> Callable:
        def wrapper_cloud_watch_alarm(func: Callable):
            self._routes.append(
                CloudWatchAlarmRoute(func=func, arn=arn, alarm_name=alarm_name, alarm_name_prefix=alarm_name_prefix),
            )

        return wrapper_cloud_watch_alarm

    def cloud_watch_logs(
        self,
        log_group: str | None = None,
        log_group_prefix: str | None = None,
        log_stream: str | None = None,
        log_stream_prefix: str | None = None,
        subscription_filters: str | list[str] | None = None,
    ) -> Callable:
        def wrapper_cloud_watch_logs(func: Callable):
            self._routes.append(
                CloudWatchLogsRoute(
                    func=func,
                    log_group=log_group,
                    log_group_prefix=log_group_prefix,
                    log_stream=log_stream,
                    log_stream_prefix=log_stream_prefix,
                    subscription_filters=subscription_filters,
                ),
            )

        return wrapper_cloud_watch_logs

    def code_deploy_lifecycle_hook(self) -> Callable:
        def wrapper_code_deploy_lifecycle_hook(func: Callable):
            self._routes.append(CodeDeployLifecycleHookRoute(func=func))

        return wrapper_code_deploy_lifecycle_hook

    def event_bridge(
        self,
        detail_type: str | None = None,
        source: str | None = None,
        resources: str | list[str] | None = None,
    ) -> Callable:
        def wrap_event_bridge(func: Callable):
            self._routes.append(
                EventBridgeRoute(func=func, detail_type=detail_type, source=source, resources=resources),
            )

        return wrap_event_bridge

    def s3(
        self,
        bucket: str | None = None,
        bucket_prefix: str | None = None,
        key: str | None = None,
        key_prefix: str | None = None,
        key_suffix: str | None = None,
        event_name: str | None = None,
    ) -> Callable:
        def wrap_s3(func: Callable):
            self._routes.append(
                S3Route(
                    func=func,
                    bucket=bucket,
                    bucket_prefix=bucket_prefix,
                    key=key,
                    key_prefix=key_prefix,
                    key_suffix=key_suffix,
                    event_name=event_name,
                ),
            )

        return wrap_s3

    def secrets_manager(self, secret_id: str | None = None, secret_name_prefix: str | None = None):
        def wrap_secrets_manager(func: Callable):
            self._routes.append(
                SecretsManagerRoute(func=func, secret_id=secret_id, secret_name_prefix=secret_name_prefix),
            )

        return wrap_secrets_manager

    def ses(
        self,
        mail_to: str | list[str] | None = None,
        mail_from: str | list[str] | None = None,
        mail_subject: str | None = None,
    ) -> Callable:
        def wrap_ses(func: Callable):
            self._routes.append(SESRoute(func=func, mail_to=mail_to, mail_from=mail_from, mail_subject=mail_subject))

        return wrap_ses

    def sns(
        self,
        arn: str | None = None,
        name: str | None = None,
        name_prefix: str | None = None,
        subject: str | None = None,
        subject_prefix: str | None = None,
    ) -> Callable:
        def wrap_sns(func: Callable):
            self._routes.append(
                SNSRoute(
                    func=func,
                    arn=arn,
                    name=name,
                    name_prefix=name_prefix,
                    subject=subject,
                    subject_prefix=subject_prefix,
                ),
            )

        return wrap_sns

    def resolve_route(self, event: dict[str, Any]) -> tuple[Callable, Any] | None:
        for route in self._routes:
            data = route.match(event=event)
            if data is not None:
                return data
        return None
