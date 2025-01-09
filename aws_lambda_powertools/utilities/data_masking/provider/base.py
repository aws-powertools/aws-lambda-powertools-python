from __future__ import annotations

import functools
import json
import re
from typing import Any, Callable

# , Iterable
from aws_lambda_powertools.utilities.data_masking.constants import DATA_MASKING_STRING

PRESERVE_CHARS = set("-_. ")
_regex_cache = {}


class BaseProvider:
    """
    The BaseProvider class serves as an abstract base class for data masking providers.

    Examples
    --------
    ```
    from aws_lambda_powertools.utilities._data_masking.provider import BaseProvider
    from aws_lambda_powertools.utilities.data_masking import DataMasking

    class MyCustomProvider(BaseProvider):
        def encrypt(self, data) -> str:
            # Implementation logic for data encryption

        def decrypt(self, data) -> Any:
            # Implementation logic for data decryption

        def erase(self, data) -> str | Iterable:
            # Implementation logic for data masking
            pass

    def lambda_handler(event, context):
        provider = MyCustomProvider(["secret-key"])
        data_masker = DataMasking(provider=provider)

        data = {
            "project": "powertools",
            "sensitive": "password"
        }

        encrypted = data_masker.encrypt(data)

        return encrypted
    ```
    """

    def __init__(
        self,
        json_serializer: Callable[..., str] = functools.partial(json.dumps, ensure_ascii=False),
        json_deserializer: Callable[[str], Any] = json.loads,
    ) -> None:
        self.json_serializer = json_serializer
        self.json_deserializer = json_deserializer

    def encrypt(self, data, provider_options: dict | None = None, **encryption_context: str) -> str:
        """
        Abstract method for encrypting data. Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement encrypt()")

    def decrypt(self, data, provider_options: dict | None = None, **encryption_context: str) -> Any:
        """
        Abstract method for decrypting data. Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement decrypt()")

    def erase(
        self,
        data: Any,
        dynamic_mask: bool | None = None,
        custom_mask: str | None = None,
        regex_pattern: str | None = None,
        mask_format: str | None = None,
        masking_rules: dict | None = None,
        **kwargs,
    ) -> str | dict | list | tuple | set:
        """
        This method irreversibly erases data.

        If the data to be erased is of type `str`, `dict`, or `bytes`,
        this method will return an erased string, i.e. "*****".

        If the data to be erased is of an iterable type like `list`, `tuple`,
        or `set`, this method will return a new object of the same type as the
        input data but with each element masked according to the specified rules.
        """
        result = None

        # Handle empty or None data
        if data is None or (isinstance(data, (str, list, dict)) and not data):
            return data

        # Handle string data
        if isinstance(data, str):
            if regex_pattern and mask_format:
                result = self._regex_mask(data, regex_pattern, mask_format)
            elif custom_mask:
                result = self._pattern_mask(data, custom_mask)
            elif dynamic_mask:
                result = self._custom_erase(data, **kwargs)
            else:
                result = DATA_MASKING_STRING

        # Handle dictionary data
        elif isinstance(data, dict):
            if masking_rules:
                result = self._apply_masking_rules(data, masking_rules)
            else:
                result = {}
                for k, v in data.items():
                    result[str(k)] = self.erase(
                        str(v),
                        dynamic_mask=dynamic_mask,
                        custom_mask=custom_mask,
                        regex_pattern=regex_pattern,
                        mask_format=mask_format,
                        masking_rules=masking_rules,
                        **kwargs,
                    )

        # Handle iterable data (list, tuple, set)
        elif isinstance(data, (list, tuple, set)):
            masked_data = [
                self.erase(
                    item,
                    dynamic_mask=dynamic_mask,
                    custom_mask=custom_mask,
                    regex_pattern=regex_pattern,
                    mask_format=mask_format,
                    masking_rules=masking_rules,
                    **kwargs,
                )
                for item in data
            ]
            result = type(data)(masked_data)

        # Handle other types (int, float, bool, etc.)
        else:
            result = str(data)

        return result

    def _apply_masking_rules(self, data: dict, masking_rules: dict) -> Any:
        """Apply masking rules to dictionary data."""
        return {
            key: self.erase(str(value), **masking_rules[key]) if key in masking_rules else str(value)
            for key, value in data.items()
        }

    def _pattern_mask(self, data: str, pattern: str) -> str:
        """Apply pattern masking to string data."""
        return pattern[: len(data)] if len(pattern) >= len(data) else pattern

    def _regex_mask(self, data: str, regex_pattern: str, mask_format: str) -> str:
        """Apply regex masking to string data."""
        try:
            if regex_pattern not in _regex_cache:
                _regex_cache[regex_pattern] = re.compile(regex_pattern)
            return _regex_cache[regex_pattern].sub(mask_format, data)
        except re.error:
            return DATA_MASKING_STRING

    def _custom_erase(self, data: str, **kwargs) -> str:
        if not data:
            return ""

        return "".join("*" if char not in PRESERVE_CHARS else char for char in data)
