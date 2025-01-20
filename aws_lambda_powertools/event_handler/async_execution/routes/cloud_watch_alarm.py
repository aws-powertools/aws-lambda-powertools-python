from __future__ import annotations

from typing import Any, Callable

from aws_lambda_powertools.utilities.data_classes.cloud_watch_alarm_event import (
    CloudWatchAlarmEvent,
)

from .base import BaseRoute


class CloudWatchAlarmRoute(BaseRoute):
    arn: str | None
    alarm_name: str | None
    alarm_name_prefix: str | None

    def __init__(
        self,
        func: Callable,
        arn: str | None = None,
        alarm_name: str | None = None,
        alarm_name_prefix: str | None = None,
    ):
        self.func = func
        self.arn = arn
        self.alarm_name = alarm_name
        self.alarm_name_prefix = alarm_name_prefix

        if not self.arn and not self.alarm_name and not self.alarm_name_prefix:
            raise ValueError("arn, alarm_name, or alarm_name_prefix must be not null")

    def is_target_with_arn(self, arn: str | None) -> bool:
        if not arn:
            return False
        elif self.arn:
            return self.arn == arn
        else:
            return False

    def is_target_with_alarm_name(self, alarm_name: str | None) -> bool:
        if not alarm_name:
            return False
        elif self.alarm_name:
            return self.alarm_name == alarm_name
        elif self.alarm_name_prefix:
            return alarm_name.find(self.alarm_name_prefix) == 0
        else:
            return False

    def match(self, event: dict[str, Any]) -> tuple[Callable, CloudWatchAlarmEvent] | None:
        if not isinstance(event, dict):
            return None

        arn: str | None = event.get("alarmArn")
        alarm_name: str | None = event.get("alarmData", {}).get("alarmName")

        if not arn and not alarm_name:
            return None

        if not self.arn:
            arn = None

        if not self.alarm_name and not self.alarm_name_prefix:
            alarm_name = None

        flag_arn = self.is_target_with_arn(arn=arn)
        flag_alarm_name = self.is_target_with_alarm_name(alarm_name=alarm_name)

        text = ", ".join(
            ["arn: x" if arn is None else "arn: o", "alarm_name: x" if alarm_name is None else "alarm_name: o"],
        )

        mapping = {
            "arn: o, alarm_name: o": flag_arn and flag_alarm_name,
            "arn: o, alarm_name: x": flag_arn,
            "arn: x, alarm_name: o": flag_alarm_name,
            "arn: x, alarm_name: x": False,
        }

        if mapping[text]:
            return self.func, CloudWatchAlarmEvent(event)
        else:
            return None
