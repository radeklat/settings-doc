from __future__ import annotations

import pytest
from click import BadParameter
from pydantic_settings import BaseSettings

from settings_doc.importing import import_class_path
from tests.fixtures.valid_settings import EmptySettings, FullSettings

_PREFIX = "Cannot read the settings class: "


class TestImportClassPath:
    @staticmethod
    @pytest.mark.parametrize(
        "class_paths, expected_classes",
        [
            pytest.param(["EmptySettings"], {EmptySettings: None}, id="single class when single option is given"),
            pytest.param(
                ["EmptySettings", "FullSettings"],
                {EmptySettings: None, FullSettings: None},
                id="multiple classes when multiple options are given",
            ),
        ],
    )
    def should_return(class_paths: list[str], expected_classes: dict[type[BaseSettings], None]):
        classes = import_class_path(tuple(f"tests.fixtures.valid_settings.{class_path}" for class_path in class_paths))
        assert classes == expected_classes

    @staticmethod
    @pytest.mark.parametrize(
        "class_path, error_message",
        [
            pytest.param(
                "tests.fixtures.module_without_settings.NotHere",
                f"{_PREFIX}module 'tests.fixtures.module_without_settings' has no attribute 'NotHere'",
                id="class with given name is not in the module",
            ),
            pytest.param(
                "not_a_module.EmptySettings",
                f"{_PREFIX}No module named 'not_a_module'",
                id="module doesn't exist",
            ),
            pytest.param(
                "..not_a_module.EmptySettings",
                f"{_PREFIX}Relative imports are not supported.",
                id="relative import is attempted",
            ),
            pytest.param(
                "src.settings_doc.main.OutputFormat",
                "Target class must be a subclass of BaseSettings but 'OutputFormat' found.",
                id="found class is not a subclass of BaseSettings",
            ),
            pytest.param(
                "src.settings_doc.main.app",
                "Target 'app' in module 'src.settings_doc.main' is not a class.",
                id="found class is not a class",
            ),
        ],
    )
    def should_fail_with_bad_parameter_when(class_path, error_message):
        with pytest.raises(BadParameter, match=error_message):
            import_class_path((class_path,))
