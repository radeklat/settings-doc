from typing import Type

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from pydantic import Field
from pydantic_settings import BaseSettings
from pytest_mock import MockerFixture

from tests.fixtures.valid_settings import (
    SETTINGS_ATTR,
    EnvNestedDelimiterSettings,
    EnvPrefixAndNestedDelimiterSettings,
    EnvPrefixSettings,
    ExamplesSettings,
    FullSettings,
    PossibleValuesSettings,
    ValidationAliasChoicesSettings,
    ValidationAliasPathSettings,
    ValidationAliasSettings,
)
from tests.helpers import run_app_with_settings


class TestDotEnvFormat:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_string, settings_class",
        [
            pytest.param(f"{SETTINGS_ATTR}=\n", ValidationAliasSettings, id="validation alias with required value"),
            pytest.param(
                f"{SETTINGS_ATTR}=some_value\n\n", FullSettings, id="variable name with optional default value"
            ),
            pytest.param("# use fullsettings like this\n", FullSettings, id="description"),
        ],
    )
    def should_generate(
        runner: CliRunner,
        mocker: MockerFixture,
        expected_string: str,
        settings_class: Type[BaseSettings],
    ):
        assert expected_string in run_app_with_settings(mocker, runner, settings_class, fmt="dotenv")

    @staticmethod
    @pytest.mark.parametrize(
        "expected_name, expected_string, settings_class",
        [
            pytest.param("literal", "`debug`, `info`", PossibleValuesSettings, id="literal"),
            pytest.param(
                "simple",
                "`debug`, `info`",
                PossibleValuesSettings,
                id="a list in json_schema_extra.possible_values",
            ),
            pytest.param(
                "simple_tuple",
                "- `debug`\n#   - `info`",
                PossibleValuesSettings,
                id="tuples with a single item in json_schema_extra.possible_values",
            ),
            pytest.param(
                "tuple_with_explanation",
                "- `debug`: debug level\n#   - `info`: info level",
                PossibleValuesSettings,
                id="tuples with two items in json_schema_extra.possible_values",
            ),
        ],
    )
    def should_generate_possible_values_from(
        runner: CliRunner,
        mocker: MockerFixture,
        expected_name: str,
        expected_string: str,
        settings_class: Type[BaseSettings],
    ):
        assert f"# possible values:\n#   {expected_string}\n{expected_name}=\n" in run_app_with_settings(
            mocker, runner, settings_class, fmt="dotenv"
        )

    @staticmethod
    def should_ignore_examples(runner: CliRunner, mocker: MockerFixture):
        assert "# examples" not in run_app_with_settings(mocker, runner, ExamplesSettings, fmt="dotenv")

    @staticmethod
    @pytest.mark.parametrize(
        "settings_class",
        [
            pytest.param(ValidationAliasPathSettings, id="validation AliasPath"),
            pytest.param(ValidationAliasChoicesSettings, id="validation AliasChoices"),
        ],
    )
    def should_log_error_for(
        runner: CliRunner,
        mocker: MockerFixture,
        settings_class: Type[BaseSettings],
        caplog: LogCaptureFixture,
    ):
        assert f"# {SETTINGS_ATTR}=" not in run_app_with_settings(mocker, runner, settings_class, fmt="dotenv")
        assert "Unsupported validation alias" in caplog.text

    @staticmethod
    def should_list_values_if_they_do_not_fit_in_75_chars(runner: CliRunner, mocker: MockerFixture):
        a_value = "a" * (75 - 2 - 4)  # -2 chars. for backticks -4 for # and indentation
        b_value = a_value.replace("a", "b") + "b"  # 1 char over the limit

        class Settings(BaseSettings):
            fits: str = Field(..., json_schema_extra={"possible_values": [a_value]})
            fits_not: str = Field(..., json_schema_extra={"possible_values": [b_value]})
            not_values_and_descriptions: str = Field(
                ..., json_schema_extra={"possible_values": [[1, 2, 3], [4, 5, 6, 7]]}
            )

        stdout = run_app_with_settings(mocker, runner, Settings, fmt="dotenv")

        assert f"#   `{a_value}`\n" in stdout
        assert f"#   - `{b_value}`\n" in stdout
        assert "#   `[1, 2, 3]`, `[4, 5, 6, 7]`\n" in stdout

    @staticmethod
    def should_show_env_prefix(runner: CliRunner, mocker: MockerFixture):
        assert "prefix_logging_level=" in run_app_with_settings(mocker, runner, EnvPrefixSettings, fmt="dotenv")

    @staticmethod
    def should_generate_env_nested_delimiter(runner: CliRunner, mocker: MockerFixture):
        actual_string = run_app_with_settings(mocker, runner, EnvNestedDelimiterSettings, fmt="dotenv")

        assert "direct=" in actual_string
        assert "sub_model__nested=" in actual_string
        assert "sub_model__deep__leaf=" in actual_string

    @staticmethod
    def should_generate_env_prefix_and_nested_delimiter(runner: CliRunner, mocker: MockerFixture):
        actual_string = run_app_with_settings(mocker, runner, EnvPrefixAndNestedDelimiterSettings, fmt="dotenv")

        assert "prefix_direct=" in actual_string
        assert "prefix_sub_model__nested=" in actual_string
        assert "prefix_sub_model__deep__leaf=" in actual_string
