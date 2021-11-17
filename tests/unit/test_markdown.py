from typing import Any

import pytest
from pydantic import BaseSettings, Field
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from tests.fixtures.invalid_settings import PossibleValuesNotIterableSettings
from tests.fixtures.valid_settings import SETTINGS_MARKDOWN_FIRST_LINE, EmptySettings, FullSettings, RequiredSettings
from tests.helpers import run_app_with_settings


class TestMarkdownFormat:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_string",
        [
            pytest.param(f"{SETTINGS_MARKDOWN_FIRST_LINE}\n", id="variable name"),
            pytest.param("\n\n*optional*, ", id="optional flag"),
            pytest.param(", default value: `some_value`\n\n", id="default value"),
            pytest.param("\n\nuse fullsettings like this\n\n", id="description"),
            pytest.param("\n\n## examples\n\nthis is an example use\n\n", id="example"),
            pytest.param("\n\n## possible values\n\n`aaa`, `bbb`\n\n", id="possible values"),
        ],
    )
    def should_generate(runner: CliRunner, mocker: MockerFixture, expected_string: str):
        assert expected_string in run_app_with_settings(mocker, runner, FullSettings)

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
            fits: str = Field(..., possible_values=[a_value])
            fits_not: str = Field(..., possible_values=[b_value])
            not_values_and_descriptions: str = Field(..., possible_values=[(1, 2, 3), (4, 5, 6, 7)])

        stdout = run_app_with_settings(mocker, runner, Settings)

        assert f"\n\n`{a_value}`\n\n" in stdout
        assert f"\n\n- `{b_value}`\n\n" in stdout
        assert "\n\n`(1, 2, 3)`, `(4, 5, 6, 7)`\n\n" in stdout

    @staticmethod
    @pytest.mark.parametrize(
        "possible_values, expected_string",
        [
            pytest.param(
                [("name1", "description1"), ("no_description_name",)],
                "- `name1`: description1\n- `no_description_name`",
                id="tuples of 1-2 items as values and optional descriptions",
            ),
        ],
    )
    def should_list_values_for(runner: CliRunner, mocker: MockerFixture, possible_values: Any, expected_string: str):
        class Settings(BaseSettings):
            var: str = Field(..., possible_values=possible_values)

        assert f"## possible values\n\n{expected_string}\n\n" in run_app_with_settings(mocker, runner, Settings)

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
    def should_abort_when_possible_values_are_not_iterable(runner: CliRunner, mocker: MockerFixture):
        stdout = run_app_with_settings(mocker, runner, PossibleValuesNotIterableSettings)
        assert "`possible_values` must be iterable" in stdout
        assert "`123456`" in stdout
        assert "aborted" in stdout
