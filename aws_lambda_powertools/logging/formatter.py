import json
import logging
from typing import Any


def json_formatter(unserializable_value: Any):
    """JSON custom serializer to cast unserializable values to strings.

    Example
    -------

    **Serialize unserializable value to string**

        class X: pass
        value = {"x": X()}

        json.dumps(value, default=json_formatter)

    Parameters
    ----------
    unserializable_value: Any
        Python object unserializable by JSON
    """
    return str(unserializable_value)


class JsonFormatter(logging.Formatter):
    """AWS Lambda Logging formatter.

    Formats the log message as a JSON encoded string.  If the message is a
    dict it will be used directly.  If the message can be parsed as JSON, then
    the parse d value is used in the output record.

    Originally taken from https://gitlab.com/hadrien/aws_lambda_logging/

    """

    def __init__(self, **kwargs):
        """Return a JsonFormatter instance.

        The `json_default` kwarg is used to specify a formatter for otherwise
        unserializable values.  It must not throw.  Defaults to a function that
        coerces the value to a string.

        Other kwargs are used to specify log field format strings.
        """
        self.default_json_formatter = kwargs.pop("json_default", json_formatter)
        datefmt = kwargs.pop("datefmt", None)

        super(JsonFormatter, self).__init__(datefmt=datefmt)
        self.reserved_keys = ["timestamp", "level", "location"]
        self.format_dict = {
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "location": "%(funcName)s:%(lineno)d",
        }
        self.format_dict.update(kwargs)

    def update_formatter(self, **kwargs):
        self.format_dict.update(kwargs)

    def format(self, record):  # noqa: A003
        record_dict = record.__dict__.copy()
        record_dict["asctime"] = self.formatTime(record, self.datefmt)

        log_dict = {}

        for key, value in self.format_dict.items():
            if value and key in self.reserved_keys:
                # converts default logging expr to its record value
                # e.g. '%(asctime)s' to '2020-04-24 09:35:40,698'
                log_dict[key] = value % record_dict
            else:
                log_dict[key] = value

        if isinstance(record_dict["msg"], dict):
            log_dict["message"] = record_dict["msg"]
        else:
            log_dict["message"] = record.getMessage()

            # Attempt to decode the message as JSON, if so, merge it with the
            # overall message for clarity.
            try:
                log_dict["message"] = json.loads(log_dict["message"])
            except (json.decoder.JSONDecodeError, TypeError, ValueError):
                pass

        if record.exc_info and not record.exc_text:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            # from logging.Formatter:format
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            log_dict["exception"] = record.exc_text

        return json.dumps(log_dict, default=self.default_json_formatter)
