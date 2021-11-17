from typing import List, Set, Tuple, Type

import pytest
from _pytest.capture import CaptureFixture
from click import BadParameter
from pydantic import BaseSettings

from settings_doc.importing import import_module_path
from tests.fixtures.example_settings import (
    EmptySettings,
    FullSettings,
    PossibleValuesNotIterableSettings,
    RequiredSettings,
)
from tests.fixtures.example_settings_single_class import SingleSettingsInModule

_PREFIX = "Cannot read the module: "


class TestImportModulePath:
    @staticmethod
    @pytest.mark.parametrize(
        "module_paths, expected_classes",
        [
            pytest.param(
                ("example_settings_single_class",),
                {SingleSettingsInModule},
                id="for a module with a single matching class",
            ),
            pytest.param(
                ("example_settings",),
                {EmptySettings, FullSettings, RequiredSettings, PossibleValuesNotIterableSettings},
                id="for a module with multiple matching classes",
            ),
            pytest.param(
                ("example_settings", "example_settings_single_class"),
                {
                    EmptySettings,
                    FullSettings,
                    RequiredSettings,
                    PossibleValuesNotIterableSettings,
                    SingleSettingsInModule,
                },
                id="for multiple modules with multiple matching classes",
            ),
        ],
    )
    def should_return_base_settings_classes(
        module_paths: Tuple[str, ...], expected_classes: Set[Type[BaseSettings]], capsys: CaptureFixture
    ):
        classes = import_module_path(tuple(f"tests.fixtures.{module_path}" for module_path in module_paths))
        assert classes == expected_classes
        assert capsys.readouterr().err == ""

    @staticmethod
    @pytest.mark.parametrize(
        "class_paths, error_message",
        [
            pytest.param(
                ("tests.fixtures.example_settings_no_class",),
                f"No `pydantic.BaseSettings` subclasses found in module 'tests.fixtures.example_settings_no_class'.",
                id="no BaseSettings subclass is found in the module",
            ),
            pytest.param(
                ("tests.fixtures.example_settings_no_class", "tests.fixtures.example_settings_no_class2"),
                f"No `pydantic.BaseSettings` subclasses found in any of the modules.",
                id="no BaseSettings subclass is found in any of the modules",
            ),
            pytest.param(
                ("not_a_module",),
                f"{_PREFIX}No module named 'not_a_module'",
                id="module doesn't exist",
            ),
            pytest.param(
                ("..not_a_module",),
                f"{_PREFIX}Relative imports are not supported.",
                id="relative import is attempted",
            ),
        ],
    )
    def should_fail_with_bad_parameter_when(class_paths: Tuple[str, ...], error_message: str):
        with pytest.raises(BadParameter, match=error_message):
            import_module_path(class_paths)

    @staticmethod
    def should_warn_when_some_modules_have_no_classes(capsys: CaptureFixture):
        error_msg = "No `pydantic.BaseSettings` subclasses found in module 'tests.fixtures.example_settings_no_class'."
        class_paths = ("tests.fixtures.example_settings_no_class", "tests.fixtures.example_settings_single_class")
        classes = import_module_path(class_paths)
        assert classes == {SingleSettingsInModule}
        assert error_msg in capsys.readouterr().err
