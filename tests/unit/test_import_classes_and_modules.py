from typing import Set, Type

import pytest
from pydantic import BaseSettings
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from settings_doc.main import app
from tests.fixtures.module_with_single_settings_class import SingleSettingsInModule
from tests.fixtures.module_with_single_settings_class_2 import SecondarySingleSettingsInModule
from tests.fixtures.valid_settings import FullSettings, RequiredSettings

_PREFIX = "Cannot read the settings class: "


class TestImportClassesAndModules:
    @staticmethod
    @pytest.mark.parametrize(
        "class_settings, module_settings",
        [
            pytest.param({FullSettings}, {SingleSettingsInModule}, id="with a single class and a single module option"),
            pytest.param(
                {FullSettings, RequiredSettings},
                {SingleSettingsInModule, SecondarySingleSettingsInModule},
                id="with multiple class and multiple module options",
            ),
        ],
    )
    def should_generate_output_from_all_classes(
        class_settings: Set[Type[BaseSettings]],
        module_settings: Set[Type[BaseSettings]],
        runner: CliRunner,
        mocker: MockerFixture,
    ):
        all_classes = class_settings.union(module_settings)
        mocker.patch("settings_doc.importing.import_class_path", return_value=class_settings)
        mocker.patch("settings_doc.importing.import_module_path", return_value=module_settings)
        result = runner.invoke(
            app,
            [
                "generate",
                "--class",
                "THIS_SHOULD_NOT_BE_USED",
                "--module",
                "THIS_SHOULD_NOT_BE_USED_EITHER",
                "--output-format",
                "markdown",
            ],
            catch_exceptions=False,
        )
        output = result.stdout.lower()

        for settings_class in all_classes:
            assert settings_class.__name__.lower() in output

    @staticmethod
    def should_fail_when_no_classes_nor_modules_are_specified(runner: CliRunner):
        result = runner.invoke(app, ["generate", "--output-format", "markdown"], catch_exceptions=False)
        assert "No sources of data were specified" in result.output
