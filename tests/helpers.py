from __future__ import annotations

from collections.abc import Iterable as IterableCollection
from typing import Iterable, Literal

from click.testing import CliRunner, Result
from jinja2 import Environment, Template
from pydantic_settings import BaseSettings
from pytest_mock import MockerFixture

from settings_doc.main import app


def _mock_import_path(
    path_type: Literal["class", "module"],
    mocker: MockerFixture,
    settings: type[BaseSettings] | Iterable[type[BaseSettings]],
) -> None:
    if not isinstance(settings, IterableCollection):
        settings = [settings]

    settings = {_: None for _ in settings}
    mocker.patch(f"settings_doc.importing.import_{path_type}_path", return_value=settings)


def mock_import_class_path(mocker: MockerFixture, settings: type[BaseSettings] | Iterable[type[BaseSettings]]) -> None:
    _mock_import_path("class", mocker, settings)


def mock_import_module_path(mocker: MockerFixture, settings: type[BaseSettings] | Iterable[type[BaseSettings]]) -> None:
    _mock_import_path("module", mocker, settings)


def run_app_with_settings(
    mocker: MockerFixture,
    runner: CliRunner,
    settings: type[BaseSettings] | Iterable[type[BaseSettings]],
    args: list[str] | None = None,
    fmt: str = "markdown",
    template: str | Template | None = None,
) -> str:
    """Helper function to run common app scenarios.

    Args:
        mocker: pytest mocker from the test case.
        runner: CLI runner from the test case.
        settings: One or more settings classes to used for generating documentation.
        args: Additional positional arguments given to the app.
        fmt: Format to use.
        template: A custom template to use. When specified, the template getter will be
            mocked and therefore the ``fmt`` argument ignored. You can use
            ``jinja2.Environment`` methods to create a ``Template`` or provide a template
            as a string.

    Returns:
        Lower-cased stdout of the app.
    """
    if template:
        assert fmt == "markdown", "The `fmt` argument is ignored when `template` is used."
        if isinstance(template, str):
            template = Environment().from_string(template)
        mocker.patch("settings_doc.main.get_template", return_value=template)

    if args is None:
        args = []

    mock_import_class_path(mocker, settings)

    result = runner.invoke(
        app, ["generate", "--class", "THIS_SHOULD_NOT_BE_USED", "--output-format", fmt] + args, catch_exceptions=False
    )
    return result.stdout.lower()


def copy_templates(runner: CliRunner, folder: str) -> Result:
    return runner.invoke(app, ["templates", "--copy-to", folder], catch_exceptions=False)
