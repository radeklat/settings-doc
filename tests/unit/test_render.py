from typing import Type

import pytest
from pydantic_settings import BaseSettings
from pytest_mock import MockerFixture

from settings_doc import OutputFormat, render
from tests.fixtures.valid_settings import SETTINGS_ATTR, FullSettings, ValidationAliasSettings
from tests.helpers import mock_import_class_path, mock_import_module_path


class TestRenderDotEnvFormat:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_string, settings_class",
        [
            pytest.param(f"{SETTINGS_ATTR}=\n", ValidationAliasSettings, id="validation alias with required value"),
            pytest.param(
                f"{SETTINGS_ATTR}=some_value\n\n", FullSettings, id="variable name with optional default value"
            ),
            pytest.param("# use fullsettings like this\n", FullSettings, id="description"),
        ],
    )
    def should_generate_from_class_path(
        mocker: MockerFixture, expected_string: str, settings_class: Type[BaseSettings]
    ):
        mock_import_class_path(mocker, settings_class)
        assert expected_string in render(OutputFormat.DOTENV, class_path=("MockSettings",)).lower()

    @staticmethod
    @pytest.mark.parametrize(
        "expected_string, settings_class",
        [
            pytest.param(f"{SETTINGS_ATTR}=\n", ValidationAliasSettings, id="validation alias with required value"),
            pytest.param(
                f"{SETTINGS_ATTR}=some_value\n\n", FullSettings, id="variable name with optional default value"
            ),
            pytest.param("# use fullsettings like this\n", FullSettings, id="description"),
        ],
    )
    def should_generate_from_module_path(
        mocker: MockerFixture, expected_string: str, settings_class: Type[BaseSettings]
    ):
        mock_import_module_path(mocker, settings_class)
        assert expected_string in render(OutputFormat.DOTENV, module_path=("MockSettings",)).lower()

    @staticmethod
    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({}, id="class_path unset, module_path unset"),
            pytest.param({"class_path": []}, id="class_path empty, module_path unset"),
            pytest.param({"module_path": []}, id="module_path empty, class_path unset"),
            pytest.param({"class_path": [], "module_path": []}, id="class_path and module_path empty"),
        ],
    )
    def should_raise_value_error_when_no_source_data_specified(kwargs):
        with pytest.raises(ValueError, match="No sources of data were specified."):
            render(OutputFormat.DOTENV, **kwargs)

    @staticmethod
    def should_raise_value_error_when_source_data_is_empty(mocker: MockerFixture):
        mock_import_class_path(mocker, [])
        with pytest.raises(ValueError, match="No sources of data were found."):
            render(OutputFormat.DOTENV, class_path=("MockSettings",))
