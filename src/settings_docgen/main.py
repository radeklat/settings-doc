import importlib
from collections.abc import Iterable as IterableCollection
from enum import Enum, auto
from functools import lru_cache
from inspect import isclass
from pathlib import Path
from typing import Any, Type

from click import Abort, BadParameter, secho
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseSettings
from typer import Option, Typer, colors

app = Typer()


class OutputFormat(Enum):
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):  # pylint: disable=no-self-argument
        del start, count, last_values
        return name.lower()  # pylint: disable=no-member

    DOTENV = auto()
    MARKDOWN = auto()
    DEBUG = auto()


@lru_cache(maxsize=None)  # Python 3.9+: use functools.cache
def import_class_path(class_path: str) -> Type[BaseSettings]:
    module, class_name = class_path.rsplit(".", maxsplit=1)
    try:
        settings = getattr(importlib.import_module(module), class_name)
    except (AttributeError, ModuleNotFoundError, TypeError) as exc:
        cause = str(exc)
        if isinstance(exc, TypeError) and "relative import" in cause:
            cause = "Relative imports are not supported."
        raise BadParameter(f"Cannot read the settings class: {cause}") from exc

    if not isclass(settings):
        raise BadParameter(f"Target '{class_name}' in module '{module}' is not a class.")

    if not issubclass(settings, BaseSettings):
        raise BadParameter(f"Target class must be a subclass of BaseSettings but '{settings.__name__}' found.")

    return settings


def class_path_callback(value: str) -> str:
    import_class_path(value)
    return value


def is_values_with_descriptions(value: Any) -> bool:
    if not isinstance(value, IterableCollection):
        secho(f"`possible_values` must be iterable but `{value}` used.", fg=colors.RED)
        raise Abort()

    return all(list(map(lambda item: isinstance(item, tuple) and 2 >= len(item) >= 1, value)))


@app.command()
def main(
    class_path: str = Option(
        ...,
        "--class",
        "-c",
        callback=class_path_callback,
        help="Period-separated import path to a subclass of `pydantic.BaseSettings`. "
        "Must be importable from current working directory.",
    ),
    output_format: OutputFormat = Option(..., "--output-format", "-f", help="Output format."),
    heading_offset: int = Option(0, min=0, help="How nested should be the top level heading generated."),
):
    """Formats `pydantic.BaseSettings` into various formats."""
    settings = import_class_path(class_path)
    render_kwargs = {"heading_offset": heading_offset, "fields": settings.__fields__.values()}

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["is_values_with_descriptions"] = is_values_with_descriptions
    template = env.get_template(f"{output_format.value}.jinja")

    print(template.render(**render_kwargs))


if __name__ == "__main__":
    app()
