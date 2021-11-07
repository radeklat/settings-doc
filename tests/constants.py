from pathlib import Path

import toml

PYPROJECT = toml.load(Path(__file__).parent.parent / "pyproject.toml")
PROJECT = PYPROJECT["tool"]["poetry"]
PROJECT_NAME = PROJECT["name"]
PROJECT_VERSION = PROJECT["version"]
