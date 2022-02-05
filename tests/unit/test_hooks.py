from typing import Type, Tuple, Callable, Iterable

import pytest
from click.testing import CliRunner
from jinja2 import Environment
from pydantic import BaseSettings
from pytest_mock import MockerFixture

from settings_doc.hooks import HOOK_PRE_RENDER, HOOK_INITIALIZE_ENVIRONMENT

from tests.fixtures.valid_settings import EmptySettings, FullSettings, \
    RequiredSettings
from tests.helpers import run_app_with_settings

_TEMPLATE_USING_TITLE = """
{% for title in titles %}
# {{ title }}
{% endfor %}
"""


_TEMPLATE_GETTING_TITLE = """
{% for cls in classes.keys() %}
# {{ get_class_title(cls) }}
{% endfor %}
"""


def get_title(cls: Type[BaseSettings]) -> str:
    return cls.Config.title if getattr(getattr(cls, 'Config', None), 'title', None) else cls.__name__


def hook_pre_render(render_kwargs: dict) -> dict:
    # Sort classes by their titles
    render_kwargs["titles"] = list(get_title(cls) for cls in render_kwargs["classes"])

    return render_kwargs


def hook_initialize_environment(env: Environment) -> None:
    env.globals["get_class_title"] = get_title


class TestRunHooks:
    @staticmethod
    @pytest.mark.parametrize(
        "hooks, template",
        [
            pytest.param(
                [(HOOK_PRE_RENDER, hook_pre_render)],
                _TEMPLATE_USING_TITLE,
                id="with pre render"
            ),
            pytest.param(
                [(HOOK_INITIALIZE_ENVIRONMENT, hook_initialize_environment)],
                _TEMPLATE_GETTING_TITLE,
                id="with env global"
            ),
        ]
    )
    def should_render_title(hooks: Iterable[Tuple[str, Callable]], template: str, runner: CliRunner, mocker: MockerFixture):
        classes = [EmptySettings, FullSettings, RequiredSettings]

        result = run_app_with_settings(mocker, runner, classes, hooks=hooks, template=template)

        for cls in classes:
            assert f"# {cls.Config.title.lower()}\n" in result
