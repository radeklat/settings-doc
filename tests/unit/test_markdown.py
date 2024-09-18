import sys
from typing import Type

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from pydantic import Field
from pydantic_settings import BaseSettings
from pytest_mock import MockerFixture

from tests.fixtures.invalid_settings import ExamplesNotIterableSettings
from tests.fixtures.valid_settings import (
    SETTINGS_MARKDOWN_FIRST_LINE,
    EmptySettings,
    EnvNestedDelimiterSettings,
    EnvPrefixAndNestedDelimiterSettings,
    EnvPrefixSettings,
    ExamplesSettings,
    FullSettings,
    MultipleSettings,
    PossibleValuesSettings,
    RequiredSettings,
    SettingsWithSettingsSubModel,
    SettingsWithSettingsSubModelNoPrefixOrDelimiter,
    ValidationAliasChoicesSettings,
    ValidationAliasPathSettings,
    ValidationAliasSettings,
)
from tests.helpers import run_app_with_settings


class TestMarkdownFormat:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_string, settings_class",
        [
            pytest.param(f"{SETTINGS_MARKDOWN_FIRST_LINE}\n", FullSettings, id="variable name"),
            pytest.param(f"{SETTINGS_MARKDOWN_FIRST_LINE}\n", ValidationAliasSettings, id="validation alias"),
            pytest.param("\n\n*optional*, ", FullSettings, id="optional flag"),
            pytest.param(", default value: `some_value`\n\n", FullSettings, id="default value"),
            pytest.param("\n\nuse fullsettings like this\n\n", FullSettings, id="description"),
            pytest.param("\n\n## examples\n\n`aaa`, `bbb`\n\n", FullSettings, id="examples"),
        ],
    )
    def should_generate(
        runner: CliRunner,
        mocker: MockerFixture,
        expected_string: str,
        settings_class: Type[BaseSettings],
    ):
        assert expected_string in run_app_with_settings(mocker, runner, settings_class)

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
                "- `debug`\n- `info`",
                PossibleValuesSettings,
                id="tuples with a single item in json_schema_extra.possible_values",
            ),
            pytest.param(
                "tuple_with_explanation",
                "- `debug`: debug level\n- `info`: info level",
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
        assert (
            f"# `{expected_name}`\n\n**required**\n\n## possible values\n\n{expected_string}\n\n"
            in run_app_with_settings(mocker, runner, settings_class)
        )

    @staticmethod
    @pytest.mark.parametrize(
        "expected_name, expected_string, settings_class",
        [
            pytest.param("only_values", "`debug`, `info`", ExamplesSettings, id="examples attribute"),
            pytest.param("structured_text", "debug, info", ExamplesSettings, id="str in json_schema_extra.examples"),
            pytest.param(
                "simple",
                "`debug`, `info`",
                ExamplesSettings,
                id="a list in json_schema_extra.examples",
            ),
            pytest.param(
                "simple_tuple",
                "- `debug`\n- `info`",
                ExamplesSettings,
                id="tuples with a single item in json_schema_extra.examples",
            ),
            pytest.param(
                "tuple_with_explanation",
                "- `debug`: debug level\n- `info`: info level",
                ExamplesSettings,
                id="tuples with two items in json_schema_extra.examples",
            ),
        ],
    )
    def should_generate_example_from(
        runner: CliRunner,
        mocker: MockerFixture,
        expected_name: str,
        expected_string: str,
        settings_class: Type[BaseSettings],
    ):
        assert f"# `{expected_name}`\n\n**required**\n\n## examples\n\n{expected_string}\n\n" in run_app_with_settings(
            mocker, runner, settings_class
        )

    @staticmethod
    def should_generate_possible_values_and_examples(runner: CliRunner, mocker: MockerFixture):
        expected_string = (
            "# `possible_values_and_examples`\n\n"
            "**required**\n\n"
            "## examples\n\n"
            "- `debug`: debug level\n- `info`: info level\n\n"
            "## possible values\n\n"
            "- `debug`: debug level\n- `info`: info level\n\n"
        )
        assert expected_string in run_app_with_settings(mocker, runner, ExamplesSettings)

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
        assert f"{SETTINGS_MARKDOWN_FIRST_LINE}\n" not in run_app_with_settings(mocker, runner, settings_class)
        assert "Unsupported validation alias" in caplog.text

    @staticmethod
    def should_generate_required_flag(runner: CliRunner, mocker: MockerFixture):
        stdout = run_app_with_settings(mocker, runner, RequiredSettings)

        assert "\n\n**required**\n\n" in stdout
        assert "\n\n*optional*, " not in stdout

    @staticmethod
    def should_list_values_if_they_do_not_fit_in_75_chars(runner: CliRunner, mocker: MockerFixture):
        a_value = "a" * 73
        b_value = "b" * 74

        class Settings(BaseSettings):
            # +2 chars. for backticks
            fits: str = Field(..., examples=[a_value])
            fits_not: str = Field(..., examples=[b_value])
            not_values_and_descriptions: str = Field(..., examples=[(1, 2, 3), (4, 5, 6, 7)])

        stdout = run_app_with_settings(mocker, runner, Settings)

        assert f"\n\n`{a_value}`\n\n" in stdout
        assert f"\n\n- `{b_value}`\n\n" in stdout
        assert "\n\n`(1, 2, 3)`, `(4, 5, 6, 7)`\n\n" in stdout

    @staticmethod
    def should_not_show_missing_description_example_possible_and_default_values(
        runner: CliRunner, mocker: MockerFixture
    ):
        expected_string = f"{SETTINGS_MARKDOWN_FIRST_LINE}\n**required**\n\n"
        assert run_app_with_settings(mocker, runner, EmptySettings) == expected_string

    @staticmethod
    def should_offset_headings_if_requested(runner: CliRunner, mocker: MockerFixture):
        expected_string = f"#{SETTINGS_MARKDOWN_FIRST_LINE}"
        assert expected_string in run_app_with_settings(mocker, runner, EmptySettings, ["--heading-offset", "1"])

    @staticmethod
    def should_abort_when_examples_are_not_iterable_nor_string(runner: CliRunner, mocker: MockerFixture):
        stdout = run_app_with_settings(mocker, runner, ExamplesNotIterableSettings)
        assert "`examples` must be iterable" in stdout
        assert "`123456`" in stdout
        assert "aborted" in stdout

    @staticmethod
    def should_put_empty_line_before_second_header(runner: CliRunner, mocker: MockerFixture):
        stdout = run_app_with_settings(mocker, runner, MultipleSettings)
        assert "\n\n# `password`\n" in stdout

    @staticmethod
    def should_end_with_a_single_empty_line(runner: CliRunner, mocker: MockerFixture):
        stdout = run_app_with_settings(mocker, runner, MultipleSettings)
        assert not stdout.endswith("`\n\n"), f"'{stdout}' ends with empty line"

    @staticmethod
    def should_show_env_prefix(runner: CliRunner, mocker: MockerFixture):
        expected_string = "# `prefix_logging_level`\n\n**required**\n\n"
        assert run_app_with_settings(mocker, runner, EnvPrefixSettings) == expected_string

    @staticmethod
    def should_generate_env_nested_delimiter(runner: CliRunner, mocker: MockerFixture):
        actual_string = run_app_with_settings(mocker, runner, EnvNestedDelimiterSettings)

        assert "`direct`" in actual_string
        assert "`sub_model__nested`" in actual_string
        assert "`sub_model__deep__leaf`" in actual_string

    @staticmethod
    def should_generate_env_prefix_and_nested_delimiter(runner: CliRunner, mocker: MockerFixture):
        actual_string = run_app_with_settings(mocker, runner, EnvPrefixAndNestedDelimiterSettings)

        assert "`prefix_direct`" in actual_string
        assert "`prefix_sub_model__nested`" in actual_string
        assert "`prefix_sub_model__deep__leaf`" in actual_string

    @staticmethod
    def should_generate_settings_with_settings_sub_model(runner: CliRunner, mocker: MockerFixture):
        actual_string = run_app_with_settings(mocker, runner, SettingsWithSettingsSubModel)

        assert "`prefix_direct`" in actual_string
        assert "`prefix_sub_model_nested`" in actual_string
        assert "`prefix_sub_model_sub_model_2__leaf`" in actual_string
        assert "prefix_nested" not in actual_string
        assert "prefix_leaf" not in actual_string
        assert "prefix_sub_model_direct" not in actual_string
        assert "prefix_sub_model_leaf" not in actual_string
        assert "prefix_sub_model_1" not in actual_string
        assert "prefix_sub_model_sub_model_2__direct" not in actual_string
        assert "prefix_sub_model_sub_model_2__nested" not in actual_string
        assert "prefix_sub_model_sub_model_2__sub_model_1" not in actual_string

    @staticmethod
    def should_generate_settings_with_settings_sub_model_no_prefix_or_delimiter(
        runner: CliRunner, mocker: MockerFixture
    ):
        actual_string = run_app_with_settings(mocker, runner, SettingsWithSettingsSubModelNoPrefixOrDelimiter)

        assert "`leaf`" in actual_string
        assert "my_leaf" not in actual_string


@pytest.mark.skipif(sys.version_info < (3, 11), reason="StrEnum is not available in Python 3.10 and below")
class TestMarkdownFormatFromStrEnum:
    @staticmethod
    def should_generate_default_value(runner: CliRunner, mocker: MockerFixture, str_enum_settings: Type[BaseSettings]):
        expected_string = "# `logging_level`\n\n*optional*, default value: `debug`\n\n"
        assert expected_string in run_app_with_settings(mocker, runner, str_enum_settings)

    @staticmethod
    def should_generate_possible_values(
        runner: CliRunner, mocker: MockerFixture, str_enum_settings: Type[BaseSettings]
    ):
        expected_string = "## possible values\n\n`debug`, `info`"
        assert expected_string in run_app_with_settings(mocker, runner, str_enum_settings)


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="StrEnum should be used in Python 3.11 and above")
class TestMarkdownFormatFromStrSubclassedEnum:
    @staticmethod
    def should_generate_default_value_from_str_subclass_enums(
        runner: CliRunner, mocker: MockerFixture, str_enum_subclass_settings: Type[BaseSettings]
    ):
        expected_string = "# `logging_level`\n\n*optional*, default value: `debug`\n\n"
        assert expected_string in run_app_with_settings(mocker, runner, str_enum_subclass_settings)

    @staticmethod
    def should_generate_possible_values(
        runner: CliRunner, mocker: MockerFixture, str_enum_subclass_settings: Type[BaseSettings]
    ):
        expected_string = "## possible values\n\n`debug`, `info`"
        assert expected_string in run_app_with_settings(mocker, runner, str_enum_subclass_settings)


class TestMarkdownFormatFromIntEnum:
    @staticmethod
    def should_generate_default_value(runner: CliRunner, mocker: MockerFixture, int_enum_settings: Type[BaseSettings]):
        expected_string = "# `logging_level`\n\n*optional*, default value: `10`\n\n"
        assert expected_string in run_app_with_settings(mocker, runner, int_enum_settings)

    @staticmethod
    def should_generate_possible_values(
        runner: CliRunner, mocker: MockerFixture, int_enum_settings: Type[BaseSettings]
    ):
        expected_string = "## possible values\n\n`10`, `20`"
        assert expected_string in run_app_with_settings(mocker, runner, int_enum_settings)
