from typing import Set, Tuple, Type

import pytest
from _pytest.capture import CaptureFixture
from click import BadParameter
from pydantic_settings import BaseSettings

from settings_doc.importing import import_module_path
from tests.fixtures.module_with_single_settings_class import SingleSettingsInModule
from tests.fixtures.valid_settings import (
    EmptySettings,
    FullSettings,
    LiteralSettings,
    MultipleSettings,
    RequiredSettings,
)

_PREFIX = "Cannot read the module: "


class TestImportModulePath:
    @staticmethod
    @pytest.mark.parametrize(
        "module_paths, expected_classes",
        [
            pytest.param(
                ("module_with_single_settings_class",),
                {SingleSettingsInModule},
                id="for a module with a single matching class",
            ),
            pytest.param(
                ("valid_settings",),
                {
                    EmptySettings,
                    FullSettings,
                    LiteralSettings,
                    RequiredSettings,
                    MultipleSettings,
                },
                id="for a module with multiple matching classes",
            ),
            pytest.param(
                ("valid_settings", "module_with_single_settings_class"),
                {
                    EmptySettings,
                    FullSettings,
                    LiteralSettings,
                    RequiredSettings,
                    SingleSettingsInModule,
                    MultipleSettings,
                },
                id="for multiple modules with multiple matching classes",
            ),
        ],
    )
    def should_return_base_settings_classes(
        module_paths: Tuple[str, ...],
        expected_classes: Set[Type[BaseSettings]],
        capsys: CaptureFixture,
    ):
        classes = import_module_path(tuple(f"tests.fixtures.{module_path}" for module_path in module_paths))
        assert classes == expected_classes
        assert capsys.readouterr().err == ""

    @staticmethod
    @pytest.mark.parametrize(
        "class_paths, error_message",
        [
            pytest.param(
                ("tests.fixtures.module_without_settings",),
                "No `pydantic.BaseSettings` subclasses found in module 'tests.fixtures.module_without_settings'.",
                id="no BaseSettings subclass is found in the module",
            ),
            pytest.param(
                (
                    "tests.fixtures.module_without_settings",
                    "tests.fixtures.module_without_settings_2",
                ),
                "No `pydantic.BaseSettings` subclasses found in any of the modules.",
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
        error_msg = "No `pydantic.BaseSettings` subclasses found in module 'tests.fixtures.module_without_settings'."
        class_paths = (
            "tests.fixtures.module_without_settings",
            "tests.fixtures.module_with_single_settings_class",
        )
        classes = import_module_path(class_paths)
        assert classes == {SingleSettingsInModule}
        assert error_msg in capsys.readouterr().err
