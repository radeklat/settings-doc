import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List

from click.testing import CliRunner
from pytest_mock import MockerFixture

from tests.fixtures.valid_settings import EmptySettings
from tests.helpers import copy_templates, run_app_with_settings


class TestTemplatesOverride:
    @staticmethod
    def should_use_templates_from_given_directories_in_priority_order(runner: CliRunner, mocker: MockerFixture):
        stdouts: Dict[str, str] = {}

        with TemporaryDirectory() as folder_low_priority, TemporaryDirectory() as folder_high_priority:
            copy_templates(runner, folder_low_priority)
            copy_templates(runner, folder_high_priority)
            files: List[str] = os.listdir(folder_low_priority)
            args = ["--templates", folder_high_priority, "--templates", folder_low_priority]

            folder_high_priority_path = Path(folder_high_priority)
            folder_low_priority_path = Path(folder_low_priority)

            file_high_priority = files[0]
            file_low_priority = files[1]
            file_default_priority = files[2]

            os.remove(folder_high_priority_path / file_low_priority)
            os.remove(folder_high_priority_path / file_default_priority)
            os.remove(folder_low_priority_path / file_default_priority)

            with open(folder_high_priority_path / file_high_priority, "w", encoding="utf-8") as file:
                file.write("High")

            with open(folder_low_priority_path / file_low_priority, "w", encoding="utf-8") as file:
                file.write("Low")

            for filename in [file_high_priority, file_low_priority, file_default_priority]:
                file_format = filename.split(".")[0]
                stdouts[filename] = run_app_with_settings(mocker, runner, EmptySettings, fmt=file_format, args=args)

        assert stdouts[file_high_priority].strip() == "high"
        assert stdouts[file_low_priority].strip() == "low"
        assert stdouts[file_default_priority]
