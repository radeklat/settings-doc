import pytest
from click import BadParameter
from pydantic import BaseSettings

from settings_docgen.main import import_class_path

_PREFIX = "Cannot read the settings class: "


class TestImportClassPath:
    @staticmethod
    def should_return_base_settings_class_when_importable():
        cls = import_class_path("tests.fixtures.example_settings.EmptySettings")
        assert issubclass(cls, BaseSettings)

    @staticmethod
    @pytest.mark.parametrize(
        "class_path, error_message",
        [
            pytest.param(
                "tests.fixtures.example_settings.NotHere",
                f"{_PREFIX}module 'tests.fixtures.example_settings' has no attribute 'NotHere'",
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
                "src.settings_docgen.main.OutputFormat",
                "Target class must be a subclass of BaseSettings but 'OutputFormat' found.",
                id="found class is not a subclass of BaseSettings",
            ),
            pytest.param(
                "src.settings_docgen.main.app",
                "Target 'app' in module 'src.settings_docgen.main' is not a class.",
                id="found class is not a class",
            ),
        ],
    )
    def should_fail_with_bad_parameter_when(class_path, error_message):
        with pytest.raises(BadParameter, match=error_message):
            import_class_path(class_path)
