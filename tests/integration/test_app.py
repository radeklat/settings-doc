from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from runpy import run_module
from subprocess import PIPE, CompletedProcess, run
from typing import Iterator
from unittest.mock import patch

import pytest

from tests.constants import PROJECT_NAME, PROJECT_VERSION
from tests.fixtures.valid_settings import SETTINGS_MARKDOWN_FIRST_LINE


def build() -> CompletedProcess:
    run(["pip", "install", "poetry"], check=False)
    return run(["poetry", "build"], check=True)


@contextmanager
def install() -> Iterator[CompletedProcess]:
    build()

    whl_file = f"{PROJECT_NAME.replace('-', '_')}-{PROJECT_VERSION}-py3-none-any.whl"
    whl_file_path = str(Path(__file__).parent.parent.parent / "dist" / whl_file)
    run(["pip", "uninstall", "-y", PROJECT_NAME], check=True)

    try:
        yield run(["pip", "install", whl_file_path], check=True)
    finally:
        run(["pip", "uninstall", "-y", PROJECT_NAME], check=True)


@contextmanager
def patch_pythonpath() -> Iterator[None]:
    pythonpath = os.getenv("PYTHONPATH", "")
    if pythonpath:
        pythonpath += ":"
    pythonpath += str(Path(__file__).parent.parent.parent)

    with patch.dict(os.environ, {"PYTHONPATH": pythonpath}):
        yield


@pytest.fixture()
def command_line_args() -> list[str]:
    return ["generate", "--class", "tests.fixtures.valid_settings.EmptySettings", "--output-format", "markdown"]


@pytest.mark.slow
class TestApp:
    @staticmethod
    def should_be_possible_to_build():
        build()

    @staticmethod
    def should_be_possible_to_install():
        with install():
            pass

    @staticmethod
    def should_be_executable(command_line_args: list[str]):
        with install():
            with patch_pythonpath():
                os.chdir(Path(__file__).parent.parent.parent)
                result = run([PROJECT_NAME] + command_line_args, stdout=PIPE, check=True)
                assert SETTINGS_MARKDOWN_FIRST_LINE in result.stdout.decode().lower()


@pytest.mark.slow
class TestMain:
    @staticmethod
    def should_be_executable(command_line_args: list[str]):
        sys.argv = [sys.argv[0]] + command_line_args
        with patch_pythonpath():
            try:
                run_module("settings_doc.main", run_name="__main__")
            except SystemExit as exc:
                if exc.code != 0:
                    raise
