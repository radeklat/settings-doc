from typing import List, Set, Type, Union

from click.testing import Result
from pydantic import BaseSettings
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from settings_doc.main import app


def run_app_with_settings(
    mocker: MockerFixture,
    runner: CliRunner,
    settings: Union[Type[BaseSettings], Set[Type[BaseSettings]]],
    args: List[str] = None,
    fmt: str = "markdown",
) -> str:
    if args is None:
        args = []
    if not isinstance(settings, set):
        settings = {settings}

    mocker.patch("settings_doc.importing.import_class_path", return_value=settings)
    result = runner.invoke(
        app, ["generate", "--class", "THIS_SHOULD_NOT_BE_USED", "--output-format", fmt] + args, catch_exceptions=False
    )
    return result.stdout.lower()


def copy_templates(runner: CliRunner, folder: str) -> Result:
    return runner.invoke(app, ["templates", "--copy-to", folder], catch_exceptions=False)
