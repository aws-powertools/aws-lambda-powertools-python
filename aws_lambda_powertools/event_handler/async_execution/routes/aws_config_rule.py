from __future__ import annotations

from typing import Any, Callable

from aws_lambda_powertools.utilities.data_classes.aws_config_rule_event import (
    AWSConfigRuleEvent,
)

from .base import BaseRoute


class AwsConfigRuleRoute(BaseRoute):
    arn: str | None
    rule_name: str | None
    rule_name_prefix: str | None
    rule_id: str | None

    def __init__(
        self,
        func: Callable,
        arn: str | None = None,
        rule_name: str | None = None,
        rule_name_prefix: str | None = None,
        rule_id: str | None = None,
    ):
        self.func = func
        self.arn = arn
        self.rule_name = rule_name
        self.rule_name_prefix = rule_name_prefix
        self.rule_id = rule_id

        if not self.arn and not self.rule_name and not self.rule_name_prefix and not self.rule_id:
            raise ValueError("arn, rule_name, rule_name_prefix, or rule_id must be not null")

    def is_target_with_arn(self, arn: str | None) -> bool:
        if not arn:
            return False
        elif self.arn:
            return self.arn == arn
        else:
            return False

    def is_target_with_rule_name(self, rule_name: str | None) -> bool:
        if not rule_name:
            return False
        elif self.rule_name:
            return self.rule_name == rule_name
        elif self.rule_name_prefix:
            return rule_name.find(self.rule_name_prefix) == 0
        else:
            return False

    def is_target_with_rule_id(self, rule_id: str | None) -> bool:
        if not rule_id:
            return False
        elif self.rule_id:
            return self.rule_id == rule_id
        else:
            return False

    def match(self, event: dict[str, Any]) -> tuple[Callable, AWSConfigRuleEvent] | None:
        if not isinstance(event, dict):
            return None

        arn = event.get("configRuleArn")
        rule_name = event.get("configRuleName")
        rule_id = event.get("configRuleId")

        if not arn and not rule_name and not rule_id:
            return None

        if not self.arn:
            arn = None

        if not self.rule_name and not self.rule_name_prefix:
            rule_name = None

        if not self.rule_id:
            rule_id = None

        flag_arn = self.is_target_with_arn(arn=arn)
        flag_rule_name = self.is_target_with_rule_name(rule_name=rule_name)
        flag_rule_id = self.is_target_with_rule_id(rule_id=rule_id)

        text = ", ".join(
            [
                "arn: x" if arn is None else "arn: o",
                "rule_name: x" if rule_name is None else "rule_name: o",
                "rule_id: x" if rule_id is None else "rule_id: o",
            ],
        )

        mapping = {
            "arn: o, rule_name: o, rule_id: o": flag_arn and flag_rule_name and flag_rule_id,
            "arn: o, rule_name: o, rule_id: x": flag_arn and flag_rule_name,
            "arn: o, rule_name: x, rule_id: o": flag_arn and flag_rule_id,
            "arn: x, rule_name: o, rule_id: o": flag_rule_name and flag_rule_id,
            "arn: o, rule_name: x, rule_id: x": flag_arn,
            "arn: x, rule_name: o, rule_id: x": flag_rule_name,
            "arn: x, rule_name: x, rule_id: o": flag_rule_id,
            "arn: x, rule_name: x, rule_id: x": False,
        }

        if mapping[text]:
            return self.func, AWSConfigRuleEvent(event)
        else:
            return None
