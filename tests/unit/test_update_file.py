import os
from tempfile import NamedTemporaryFile
from typing import Tuple

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from tests.fixtures.example_settings import EmptySettings
from tests.unit.helpers import run_app_with_settings

_OLD_CONTENT = "this is an old content"
_START_MARK = "<!-- settings-docgen START -->"
_END_MARK = "<!-- settings-docgen END -->"


def _run_app_update(mocker: MockerFixture, runner: CliRunner, content: str, *args: str) -> Tuple[str, str]:
    try:
        with NamedTemporaryFile("w", delete=False) as file:
            file.write(content)
            filename = file.name
        stdout = run_app_with_settings(mocker, runner, EmptySettings, ["--update", filename, *args])
        with open(filename, "r", encoding="utf-8") as file:
            new_content = file.read().lower()
        return stdout, new_content
    finally:
        os.remove(filename)


class TestUpdateFileOption:
    @staticmethod
    def should_overwrite_whole_file_when_no_boundaries_selected(runner: CliRunner, mocker: MockerFixture):
        stdout, new_content = _run_app_update(mocker, runner, _OLD_CONTENT)

        assert stdout == ""
        assert _OLD_CONTENT not in new_content
        assert "# `var`" in new_content

    @staticmethod
    def should_overwrite_part_of_the_file_when_between_option_set(runner: CliRunner, mocker: MockerFixture):
        prefix = "This is the beginning"
        suffix = "This is the end"
        old_content = "\n".join([prefix, _START_MARK, _OLD_CONTENT, _END_MARK, suffix])

        stdout, new_content = _run_app_update(mocker, runner, old_content, "--between", _START_MARK, _END_MARK)

        assert stdout == ""
        assert _OLD_CONTENT not in new_content
        assert "\n".join([prefix, _START_MARK, "# environment"]).lower() in new_content
        assert "\n".join(["**required**", _END_MARK, suffix]).lower() in new_content

    @staticmethod
    def should_exit_with_error_when_between_marks_not_found(runner: CliRunner, mocker: MockerFixture):
        with NamedTemporaryFile("w") as file:
            file.write(_OLD_CONTENT)
            stdout = run_app_with_settings(
                mocker, runner, EmptySettings, ["--update", file.name, "--between", _START_MARK, _END_MARK]
            )
            expected_output = (
                f"Boundary marks '{_START_MARK}' and '{_END_MARK}' not found in '{file.name}'. "
                f"Cannot update the content."
            )

        assert expected_output.lower() in stdout
