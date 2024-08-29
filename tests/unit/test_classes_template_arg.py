from click.testing import CliRunner
from pytest_mock import MockerFixture

from tests.fixtures.valid_settings import EmptySettings, FullSettings, RequiredSettings
from tests.helpers import run_app_with_settings

_TEMPLATE = """
{% for cls, fields in classes.items() %}
# {{ cls.__name__ }}
{% endfor %}
"""


class TestClassesTemplateArg:
    @staticmethod
    def should_give_access_to_classes_and_modules(runner: CliRunner, mocker: MockerFixture):
        classes = [EmptySettings, FullSettings, RequiredSettings]

        result = run_app_with_settings(mocker, runner, classes, template=_TEMPLATE)

        for cls in classes:
            assert f"# {cls.__name__.lower()}\n" in result
