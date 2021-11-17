import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from typer.testing import CliRunner

from settings_doc.main import TEMPLATES_FOLDER
from tests.helpers import copy_templates


@pytest.mark.slow
class TestTemplatesCopy:
    @staticmethod
    def should_copy_templates_into_selected_folder(runner: CliRunner):
        with TemporaryDirectory() as folder:
            result = copy_templates(runner, folder)
            files = os.listdir(folder)

        assert result.stdout == ""
        assert set(files) == set(os.listdir(TEMPLATES_FOLDER))

    @staticmethod
    def should_overwrite_existing_files(runner: CliRunner):
        with TemporaryDirectory() as folder:
            copy_templates(runner, folder)
            files = os.listdir(folder)
            filename = Path(folder) / files[0]

            with open(filename, "r", encoding="utf-8") as file:
                old_content = file.read()

            with open(filename, "w", encoding="utf-8") as file:
                file.write("existing content")

            copy_templates(runner, folder)

            with open(filename, "r", encoding="utf-8") as file:
                new_content = file.read()

        assert old_content == new_content
