from os.path import dirname, join
from pathlib import Path
from typing import Set, Tuple

import pytest
from _pytest.capture import CaptureFixture
from click import BadParameter

from settings_doc import hooks

_FIXTURES_DIR = join(dirname(dirname(dirname(__file__))), "fixtures")


class TestLoadHooks:
    @staticmethod
    @pytest.mark.parametrize(
        "file_paths, expected_hooks",
        [
            pytest.param(
                ("hooks_single",),
                {hooks.HOOK_INITIALIZE_ENVIRONMENT},
                id="for a file with a single hook",
            ),
            pytest.param(
                ("hooks_multiple",),
                {hooks.HOOK_INITIALIZE_ENVIRONMENT, hooks.HOOK_PRE_RENDER},
                id="for a file with multiple hooks",
            ),
            pytest.param(
                ("hooks_single", "hooks_single_2"),
                {hooks.HOOK_INITIALIZE_ENVIRONMENT, hooks.HOOK_PRE_RENDER},
                id="for multiple files with a single hook each",
            ),
        ],
    )
    def should_return_hooks(
        file_paths: Tuple[str, ...], expected_hooks: Set[str], capsys: CaptureFixture
    ):
        file_paths = tuple(map(lambda path: Path(_FIXTURES_DIR, path + ".py"), file_paths))
        loaded_hooks = hooks.load_hooks_from_files(file_paths)
        hooks_type = set(h[0] for h in loaded_hooks)
        assert hooks_type == expected_hooks
        assert capsys.readouterr().err == ""

    @staticmethod
    @pytest.mark.parametrize(
        "file_path, error_message",
        [
            pytest.param(
                "not_a_file",
                "File not found: ",
                id="file do not exists",
            ),
            pytest.param(
                "hooks_empty",
                "No hooks were found in file: ",
                id="file contains no hooks",
            ),
            pytest.param(
                "hooks_unknown",
                r"\w+ is not a valid hook in file:",
                id="file contains invalid hook",
            ),
        ],
    )
    def should_fail_with_bad_parameter_when(file_path, error_message):
        file_path = Path(_FIXTURES_DIR, file_path + ".py")
        with pytest.raises(BadParameter, match=error_message):
            hooks.load_hooks_from_files((file_path,))
