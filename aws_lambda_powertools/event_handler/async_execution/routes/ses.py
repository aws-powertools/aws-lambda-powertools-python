from __future__ import annotations

from typing import Any, Callable

from aws_lambda_powertools.utilities.data_classes.ses_event import SESEvent

from .base import BaseRoute


def match_prefix(all_address: list[str], all_prefix: list[str]) -> bool:
    for address in all_address:
        for prefix in all_prefix:
            if address.find(prefix) == 0:
                return True
    return False


def match_suffix(all_address: list[str], all_suffix: list[str]) -> bool:
    for address in all_address:
        for suffix in all_suffix:
            length_suffix = len(suffix)
            address_suffix = address[-length_suffix:]
            if address_suffix == suffix:
                return True
    return False


def match_prefix_and_suffix(all_address: list[str], all_prefix: list[str], all_suffix: list[str]) -> bool:
    for address in all_address:
        for prefix in all_prefix:
            for suffix in all_suffix:
                length_suffix = len(suffix)
                address_suffix = address[-length_suffix:]
                if address.find(prefix) == 0 and address_suffix == suffix:
                    return True
    return False


class SESRoute(BaseRoute):
    mail_to: list[str] | None
    mail_to_prefix: list[str] | None
    mail_to_suffix: list[str] | None
    mail_from: list[str] | None
    mail_from_prefix: list[str] | None
    mail_from_suffix: list[str] | None
    mail_subject: str | None
    mail_subject_prefix: str | None

    def __init__(
        self,
        func: Callable,
        mail_to: str | list[str] | None = None,
        mail_to_prefix: str | list[str] | None = None,
        mail_to_suffix: str | list[str] | None = None,
        mail_from: str | list[str] | None = None,
        mail_from_prefix: str | list[str] | None = None,
        mail_from_suffix: str | list[str] | None = None,
        mail_subject: str | None = None,
        mail_subject_prefix: str | None = None,
    ):
        self.func = func

        if isinstance(mail_to, str):
            self.mail_to = [mail_to]
        else:
            self.mail_to = mail_to

        if isinstance(mail_to_prefix, str):
            self.mail_to_prefix = [mail_to_prefix]
        else:
            self.mail_to_prefix = mail_to_prefix

        if isinstance(mail_to_suffix, str):
            self.mail_to_suffix = [mail_to_suffix]
        else:
            self.mail_to_suffix = mail_to_suffix

        if isinstance(mail_from, str):
            self.mail_from = [mail_from]
        else:
            self.mail_from = mail_from

        if isinstance(mail_from_prefix, str):
            self.mail_from_prefix = [mail_from_prefix]
        else:
            self.mail_from_prefix = mail_from_prefix

        if isinstance(mail_from_suffix, str):
            self.mail_from_suffix = [mail_from_suffix]
        else:
            self.mail_from_suffix = mail_from_suffix

        self.mail_subject = mail_subject
        self.mail_subject_prefix = mail_subject_prefix

        if not self.mail_to and not self.mail_from and not self.mail_subject:
            raise ValueError(
                (
                    "mail_to, mail_to_prefix, mail_to_suffix, mail_from, mail_from_prefix, mail_from_suffix, "
                    "mail_subject, or mail_subject_prefix must be not null"
                ),
            )

    def is_target_with_mail_to(self, mail_to: list[str] | None) -> bool:
        if not mail_to:
            return False
        elif self.mail_to:
            for address in mail_to:
                if address in self.mail_to:
                    return True
        elif self.mail_to_prefix and self.mail_to_suffix:
            return match_prefix_and_suffix(
                all_address=mail_to,
                all_prefix=self.mail_to_prefix,
                all_suffix=self.mail_to_suffix,
            )
        elif self.mail_to_prefix:
            return match_prefix(all_address=mail_to, all_prefix=self.mail_to_prefix)
        elif self.mail_to_suffix:
            return match_suffix(all_address=mail_to, all_suffix=self.mail_to_suffix)

        return False

    def is_target_with_mail_from(self, mail_from: list[str] | None) -> bool:
        if not mail_from:
            return False
        elif self.mail_from:
            for address in mail_from:
                if address in self.mail_from:
                    return True
        elif self.mail_from_prefix and self.mail_from_suffix:
            return match_prefix_and_suffix(
                all_address=mail_from,
                all_prefix=self.mail_from_prefix,
                all_suffix=self.mail_from_suffix,
            )
        elif self.mail_from_prefix:
            return match_prefix(all_address=mail_from, all_prefix=self.mail_from_prefix)
        elif self.mail_from_suffix:
            return match_suffix(all_address=mail_from, all_suffix=self.mail_from_suffix)

        return False

    def is_target_with_mail_subject(self, mail_subject: str | None) -> bool:
        if not mail_subject:
            return False
        elif self.mail_subject:
            return self.mail_subject == mail_subject
        elif self.mail_subject_prefix:
            return mail_subject.find(self.mail_subject_prefix) == 0
        else:
            return False

    def match(self, event: dict[str, Any]) -> tuple[Callable, SESEvent] | None:
        if not isinstance(event, dict):
            return None

        all_records: list[dict[str, Any]] = event.get("Records", [])

        if len(all_records) == 0:
            return None

        common_header: dict[str, Any] | None = all_records[0].get("ses", {}).get("mail", {}).get("commonHeaders")

        if common_header is None:
            return None

        mail_to = common_header.get("to")
        mail_from = common_header.get("from")
        mail_subject = common_header.get("subject")

        if not self.mail_to and not self.mail_to_prefix and not self.mail_to_suffix:
            mail_to = None

        if not self.mail_from and not self.mail_from_prefix and not self.mail_from_suffix:
            mail_from = None

        if not self.mail_subject and not self.mail_subject_prefix:
            mail_subject = None

        flag_mail_to = self.is_target_with_mail_to(mail_to=mail_to)
        flag_mail_from = self.is_target_with_mail_from(mail_from=mail_from)
        flag_mail_subject = self.is_target_with_mail_subject(mail_subject=mail_subject)

        text = ", ".join(
            [
                "mail_to: x" if mail_to is None else "mail_to: o",
                "mail_from: x" if mail_from is None else "mail_from: o",
                "mail_subject: x" if mail_subject is None else "mail_subject: o",
            ],
        )

        mapping = {
            "mail_to: o, mail_from: o, mail_subject: o": flag_mail_to and flag_mail_from and flag_mail_subject,
            "mail_to: o, mail_from: o, mail_subject: x": flag_mail_to and flag_mail_from,
            "mail_to: o, mail_from: x, mail_subject: o": flag_mail_to and flag_mail_subject,
            "mail_to: x, mail_from: o, mail_subject: o": flag_mail_from and flag_mail_subject,
            "mail_to: o, mail_from: x, mail_subject: x": flag_mail_to,
            "mail_to: x, mail_from: o, mail_subject: x": flag_mail_from,
            "mail_to: x, mail_from: x, mail_subject: o": flag_mail_subject,
            "mail_to: x, mail_from: x, mail_subject: x": False,
        }

        if mapping[text]:
            return self.func, SESEvent(event)
        else:
            return None
