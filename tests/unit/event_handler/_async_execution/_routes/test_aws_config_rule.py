import pytest

from aws_lambda_powertools.event_handler.async_execution.router import (
    AwsConfigRuleRoute,
)
from aws_lambda_powertools.utilities.data_classes.aws_config_rule_event import (
    AWSConfigRuleEvent,
)
from tests.functional.utils import load_event


class TestAwsConfigRuleRoute:
    def test_constructor_error(self):
        with pytest.raises(ValueError):
            AwsConfigRuleRoute(func=lambda _: None)

    @pytest.mark.parametrize(
        "option_constructor, option_func, expected",
        [
            ({"func": None, "arn": "test-arn"}, {"arn": None}, False),
            ({"func": None, "arn": "test-arn"}, {"arn": "test-arn"}, True),
            ({"func": None, "arn": "test-arn-v2"}, {"arn": "test-arn"}, False),
            ({"func": None, "rule_name": "test-rule"}, {"arn": "test-arn"}, False),
        ],
    )
    def test_is_target_with_arn(self, option_constructor, option_func, expected):
        route = AwsConfigRuleRoute(**option_constructor)
        actual = route.is_target_with_arn(**option_func)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option_func, expected",
        [
            ({"func": None, "rule_name": "test-rule"}, {"rule_name": None}, False),
            ({"func": None, "rule_name": "test-rule"}, {"rule_name": "test-rule"}, True),
            ({"func": None, "rule_name": "test-rule-v2"}, {"rule_name": "test-rule"}, False),
            ({"func": None, "rule_name_prefix": "test-r"}, {"rule_name": "test-rule"}, True),
            ({"func": None, "rule_name_prefix": "test-rr"}, {"rule_name": "test-rule"}, False),
            ({"func": None, "rule_name": "test-rule", "rule_name_prefix": "test-r"}, {"rule_name": "test-rule"}, True),
            ({"func": None, "rule_name": "test-rule", "rule_name_prefix": "test-rr"}, {"rule_name": "test-rule"}, True),
            (
                {"func": None, "rule_name": "test-rule-v2", "rule_name_prefix": "test-r"},
                {"rule_name": "test-rule"},
                False,
            ),
            (
                {"func": None, "rule_name": "test-rule-v2", "rule_name_prefix": "test-r"},
                {"rule_name": "test-rule"},
                False,
            ),
            ({"func": None, "arn": "test-arn"}, {"rule_name": "test-rule"}, False),
        ],
    )
    def test_is_target_with_rule_name(self, option_constructor, option_func, expected):
        route = AwsConfigRuleRoute(**option_constructor)
        actual = route.is_target_with_rule_name(**option_func)
        assert actual == expected

    @pytest.mark.parametrize(
        "option_constructor, option_func, expected",
        [
            ({"func": None, "rule_id": "test-id"}, {"rule_id": None}, False),
            ({"func": None, "rule_id": "test-id"}, {"rule_id": "test-id"}, True),
            ({"func": None, "rule_id": "test-id-v2"}, {"rule_id": "test-id"}, False),
            ({"func": None, "arn": "test-arn"}, {"rule_id": "test-id"}, False),
        ],
    )
    def test_is_target_with_rule_id(self, option_constructor, option_func, expected):
        route = AwsConfigRuleRoute(**option_constructor)
        actual = route.is_target_with_rule_id(**option_func)
        assert actual == expected

    @pytest.mark.parametrize(
        "event_name, option_constructor, expected_true",
        [
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, rule_name_prefix, and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, rule_name_prefix, and rule_id
            # match 3, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, rule_name_prefix, and rule_id
            # match 2, unmatch 2
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, rule_name_prefix, and rule_id
            # match 1, unmatch 3
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, rule_name_prefix, and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_name_prefix
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_name_prefix
            # match 2, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                },
                True,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_name_prefix
            # match 1, unmatch 2
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_name_prefix
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_id
            # match 2, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_id
            # match 1, unmatch 2
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name, and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name_prefix, and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name_prefix, and rule_id
            # match 2, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name_prefix, and rule_id
            # match 1, unmatch 2
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn, rule_name_prefix, and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name, rule_name_prefix, and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name, rule_name_prefix, and rule_id
            # match 2, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name, rule_name_prefix, and rule_id
            # match 1, unmatch 2
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name, rule_name_prefix, and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_name
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRule",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_name
            # match 1, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name": "MyRuleV2",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRule",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_name
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name": "MyRuleV2",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_name_prefix
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyR",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_name_prefix
            # match 1, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name_prefix": "MyR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_name_prefix
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_id": "config-rule-i9y8j9",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_id
            # match 1, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_id": "config-rule-i9y8j9",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                    "rule_id": "config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name and rule_name_prefix
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyR",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name and rule_name_prefix
            # match 1, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                    "rule_name_prefix": "MyRR",
                },
                True,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name and rule_name_prefix
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name": "MyRule", "rule_id": "config-rule-i9y8j9"},
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name and rule_id
            # match 1, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name": "MyRule", "rule_id": "config-rule-000000"},
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name": "MyRuleV2", "rule_id": "config-rule-i9y8j9"},
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name": "MyRuleV2", "rule_id": "config-rule-000000"},
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name_prefix and rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name_prefix": "MyR", "rule_id": "config-rule-i9y8j9"},
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name_prefix and rule_id
            # match 1, unmatch 1
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name_prefix": "MyR", "rule_id": "config-rule-000000"},
                False,
            ),
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name_prefix": "MyRR", "rule_id": "config-rule-i9y8j9"},
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name_prefix and rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_name_prefix": "MyRR", "rule_id": "config-rule-000000"},
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with arn
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-000000",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRule",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name": "MyRuleV2",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name_prefix
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name_prefix": "MyR",
                },
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_name_prefix
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {
                    "func": lambda *_: None,
                    "rule_name_prefix": "MyRR",
                },
                False,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_id
            # match all
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_id": "config-rule-i9y8j9"},
                True,
            ),
            # awsConfigRuleConfigurationChanged.json
            # with rule_id
            # unmatch all
            (
                "awsConfigRuleConfigurationChanged.json",
                {"func": lambda *_: None, "rule_id": "config-rule-000000"},
                False,
            ),
            # Other events
            (
                "activeMQEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "albEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "albEventPathTrailingSlash.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "albMultiValueHeadersEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "albMultiValueQueryStringEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayAuthorizerRequestEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayAuthorizerTokenEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayAuthorizerV2Event.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyEventAnotherPath.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyEventNoOrigin.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyEventPathTrailingSlash.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyEventPrincipalId.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyEvent_noVersionAuth.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyOtherEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2Event.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2EventPathTrailingSlash.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2Event_GET.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2IamEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2LambdaAuthorizerEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2OtherGetEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2SchemaMiddlwareInvalidEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apiGatewayProxyV2SchemaMiddlwareValidEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apigatewayeSchemaMiddlwareInvalidEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "apigatewayeSchemaMiddlwareValidEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "appSyncAuthorizerEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "appSyncAuthorizerResponse.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "appSyncBatchEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "appSyncDirectResolver.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "appSyncResolverEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "bedrockAgentEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "bedrockAgentEventWithPathParams.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "bedrockAgentPostEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudWatchAlarmEventCompositeMetric.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudWatchAlarmEventSingleMetric.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudWatchDashboardEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudWatchLogEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudWatchLogEventWithPolicyLevel.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudformationCustomResourceCreate.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudformationCustomResourceDelete.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cloudformationCustomResourceUpdate.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "codeDeployLifecycleHookEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "codePipelineEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "codePipelineEventData.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "codePipelineEventEmptyUserParameters.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "codePipelineEventWithEncryptionKey.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoCreateAuthChallengeEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoCustomEmailSenderEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoCustomMessageEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoCustomSMSSenderEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoDefineAuthChallengeEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoPostAuthenticationEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoPostConfirmationEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoPreAuthenticationEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoPreSignUpEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoPreTokenGenerationEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoPreTokenV2GenerationEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoUserMigrationEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "cognitoVerifyAuthChallengeResponseEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "connectContactFlowEventAll.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "connectContactFlowEventMin.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "dynamoStreamEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "eventBridgeEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kafkaEventMsk.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kafkaEventSelfManaged.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kinesisFirehoseKinesisEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kinesisFirehosePutEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kinesisFirehoseSQSEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kinesisStreamCloudWatchLogsEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kinesisStreamEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "kinesisStreamEventOneRecord.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "lambdaFunctionUrlEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "lambdaFunctionUrlEventPathTrailingSlash.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "lambdaFunctionUrlEventWithHeaders.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "lambdaFunctionUrlIAMEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "rabbitMQEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3BatchOperationEventSchemaV1.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3BatchOperationEventSchemaV2.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3Event.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventBridgeNotificationObjectCreatedEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventBridgeNotificationObjectDeletedEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventBridgeNotificationObjectExpiredEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventBridgeNotificationObjectRestoreCompletedEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventDecodedKey.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventDeleteObject.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3EventGlacier.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3ObjectEventIAMUser.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3ObjectEventTempCredentials.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "s3SqsEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "secretsManagerEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "sesEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "snsEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "snsSqsEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "snsSqsFifoEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "sqsDlqTriggerEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "sqsEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "vpcLatticeEvent.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "vpcLatticeEventPathTrailingSlash.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "vpcLatticeEventV2PathTrailingSlash.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "vpcLatticeV2Event.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
            (
                "vpcLatticeV2EventWithHeaders.json",
                {"func": None, "arn": "arn:aws:config:us-east-1:0123456789012:config-rule/config-rule-i9y8j9"},
                False,
            ),
        ],
    )
    def test_match(self, event_name, option_constructor, expected_true):
        event = load_event(file_name=event_name)
        route = AwsConfigRuleRoute(**option_constructor)
        expected_return = (route.func, AWSConfigRuleEvent(event))
        actual = route.match(event=event)
        if expected_true:
            assert actual == expected_return
        else:
            assert actual is None
