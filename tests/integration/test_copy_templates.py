import os
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner, Result

from settings_doc.main import TEMPLATES_FOLDER, app


def _copy_templates(runner: CliRunner, folder: str) -> Result:
    return runner.invoke(app, ["templates", "--copy-to", folder], catch_exceptions=False)


class TestTemplatesCopy:
    @staticmethod
    def should_copy_templates_into_selected_folder(runner: CliRunner):
        with TemporaryDirectory() as folder:
            result = _copy_templates(runner, folder)
            files = os.listdir(folder)

        assert result.stdout == ""
        assert set(files) == set(os.listdir(TEMPLATES_FOLDER))

    @staticmethod
    def should_overwrite_existing_files(runner: CliRunner):
        with TemporaryDirectory() as folder:
            _copy_templates(runner, folder)
            files = os.listdir(folder)
            filename = Path(folder) / files[0]

            with open(filename, "r", encoding="utf-8") as file:
                old_content = file.read()

            with open(filename, "w", encoding="utf-8") as file:
                file.write("existing content")

            _copy_templates(runner, folder)

            with open(filename, "r", encoding="utf-8") as file:
                new_content = file.read()

        assert old_content == new_content
