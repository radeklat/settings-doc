import importlib
import re
import shutil
from collections.abc import Iterable as IterableCollection
from enum import Enum, auto
from functools import lru_cache
from inspect import isclass
from os import listdir
from pathlib import Path
from typing import Any, List, Optional, Tuple, Type

from click import Abort, BadParameter, secho
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseSettings
from typer import Option, Typer, colors

app = Typer()


TEMPLATES_FOLDER: Path = Path(__file__).parent / "templates"


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
def generate(
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
    update_file: Optional[Path] = Option(
        None,
        "--update",
        "-u",
        exists=True,
        writable=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        help="Overwrite given file instead of writing to STDOUT. An error is raised if the "
        "file doesn't exist or is not writable. Combine this flag with the '--between' "
        "flag to update only a section of a file. ",
    ),
    update_between: Tuple[str, str] = Option(
        (None, None),
        "--between",
        help="Update file given by '--update' between these two strings. New line after "
        "the start mark/before the end mark is considered part of the pattern (if present). "
        "Without the '--update' flag, this has no effect. ",
    ),
    templates: List[Path] = Option(
        [],
        exists=True,
        readable=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="One or more folders in a priority order to use when looking up templates for "
        "generating output. Built-in templates will be used last if no matches found.",
    ),
):
    """Formats `pydantic.BaseSettings` into various formats. By default, the output is to STDOUT."""
    settings = import_class_path(class_path)
    render_kwargs = {"heading_offset": heading_offset, "fields": settings.__fields__.values()}

    env = Environment(
        loader=FileSystemLoader(templates + [TEMPLATES_FOLDER]),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["is_values_with_descriptions"] = is_values_with_descriptions
    template = env.get_template(f"{output_format.value}.jinja")
    render = template.render(**render_kwargs)

    if update_file is None:
        print(render)
        return

    with open(update_file, "r", encoding="utf-8") as file:
        content = file.read()

    with open(update_file, "w", encoding="utf-8") as file:
        if all(update_between):
            pattern = f"({re.escape(update_between[0])}\n?).*(\n?{re.escape(update_between[1])})"
            new_content = re.sub(pattern, f"\\1{render}\\2", content, count=1, flags=re.DOTALL)
            if new_content == content:
                secho(
                    f"Boundary marks '{update_between[0]}' and '{update_between[1]}' not found in '{update_file}'. "
                    f"Cannot update the content.",
                    fg=colors.RED,
                )
                raise Abort()
        else:
            new_content = render

        file.write(new_content)


@app.command("templates")
def manipulate_templates(
    copy_to: Path = Option(
        ...,
        exists=True,
        writable=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Output folder. Any existing templates with the same names with be overwritten.",
    ),
):
    """Copies built-in Jinja2 templates into a folder for modifying."""
    for file in listdir(TEMPLATES_FOLDER):
        shutil.copy2(TEMPLATES_FOLDER / file, copy_to)


if __name__ == "__main__":
    app()
