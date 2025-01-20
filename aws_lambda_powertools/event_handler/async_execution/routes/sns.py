from __future__ import annotations

from typing import Any, Callable

from aws_lambda_powertools.utilities.data_classes.sns_event import SNSEvent

from .base import BaseRoute


class SNSRoute(BaseRoute):
    arn: str | None
    name: str | None
    name_prefix: str | None
    subject: str | None
    subject_prefix: str | None

    def __init__(
        self,
        func: Callable,
        arn: str | None = None,
        name: str | None = None,
        name_prefix: str | None = None,
        subject: str | None = None,
        subject_prefix: str | None = None,
    ):
        self.func = func
        self.arn = arn
        self.name = name
        self.name_prefix = name_prefix
        self.subject = subject
        self.subject_prefix = subject_prefix

        if not self.arn and not self.name and not self.name_prefix and not self.subject and not self.subject_prefix:
            raise ValueError("arn, name, name_prefix, subject, or subject_prefix must be not null")

    def is_target_with_arn(self, arn: str | None) -> bool:
        if not arn:
            return False
        elif self.arn:
            return self.arn == arn

        part = arn.split(":")
        name = part[-1]
        if self.name:
            return self.name == name
        elif self.name_prefix:
            return name.find(self.name_prefix) == 0
        else:
            return False

    def is_target_with_subject(self, subject: str | None) -> bool:
        if not subject:
            return False
        elif self.subject:
            return self.subject == subject
        elif self.subject_prefix:
            return subject.find(self.subject_prefix) == 0
        else:
            return False

    def is_target(self, arn: str | None, subject: str | None) -> bool:
        if arn and subject:
            return self.is_target_with_arn(arn) and self.is_target_with_subject(subject)
        elif arn and not subject:
            return self.is_target_with_arn(arn)
        elif not arn and subject:
            return self.is_target_with_subject(subject)
        else:
            return False

    def match(self, event: dict[str, Any]) -> tuple[Callable, SNSEvent] | None:
        if not isinstance(event, dict):
            return None

        all_records: list[dict[str, Any]] = event.get("Records", [])

        if len(all_records) == 0:
            return None

        sns_data: dict[str, Any] | None = all_records[0].get("Sns")
        if not sns_data:
            return None

        if self.arn or self.name or self.name_prefix:
            arn = sns_data.get("TopicArn")
        else:
            arn = None

        if self.subject or self.subject_prefix:
            subject = sns_data.get("Subject")
        else:
            subject = None

        flag_arn = self.is_target_with_arn(arn=arn)
        flag_subject = self.is_target_with_subject(subject=subject)

        text = ", ".join(["arn: x" if arn is None else "arn: o", "subject: x" if subject is None else "subject: o"])

        mapping = {
            "arn: o, subject: o": flag_arn and flag_subject,
            "arn: o, subject: x": flag_arn,
            "arn: x, subject: o": flag_subject,
            "arn: x, subject: x": False,
        }

        if mapping[text]:
            return self.func, SNSEvent(event)
        else:
            return None
