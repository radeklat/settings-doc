import re
import shutil
from collections.abc import Iterable as IterableCollection
from enum import Enum, auto
from itertools import chain
from os import listdir
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type

from click import Abort, secho
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseSettings
from pydantic.fields import ModelField
from typer import Option, Typer, colors

from settings_doc import importing

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


def is_values_with_descriptions(value: Any) -> bool:
    if not isinstance(value, IterableCollection):
        secho(f"`possible_values` must be iterable but `{value}` used.", fg=colors.RED)
        raise Abort()

    return all(list(map(lambda item: isinstance(item, tuple) and 2 >= len(item) >= 1, value)))


def get_template(env: Environment, output_format: OutputFormat) -> Template:
    return env.get_template(f"{output_format.value}.jinja")


@app.command()
def generate(
    module_path: List[str] = Option(
        [],
        "--module",
        "-m",
        callback=importing.module_path_callback,
        help="Period-separated import path to a module that contains one or more subclasses"
        "of `pydantic.BaseSettings`. All such sub-classes will be used to generate the output. "
        "If that is undesirable, use the `--class` option to specify classes manually. "
        "Must be importable from current working directory. Setting PYTHONPATH appropriately "
        "may be required.",
    ),
    class_path: List[str] = Option(
        [],
        "--class",
        "-c",
        callback=importing.class_path_callback,
        help="Period-separated import path to a subclass of `pydantic.BaseSettings`. "
        "Must be importable from current working directory. Use `--module` instead to auto-discover "
        "all such subclasses in a module. Setting PYTHONPATH appropriately may be required.",
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
        help="Folder to use when looking up templates for generating output. Can be used "
        "more than once, in a priority order. Built-in templates will be used last if no "
        "matches found.",
    ),
):
    """Formats `pydantic.BaseSettings` into various formats. By default, the output is to STDOUT."""
    settings: Set[Type[BaseSettings]] = importing.import_class_path(tuple(class_path)).union(
        importing.import_module_path(tuple(module_path))
    )

    if not settings:
        secho("No sources of data were specified. Use the '--module' or '--class' options.", fg=colors.RED, err=True)
        raise Abort()

    fields: List[ModelField] = list(chain.from_iterable(cls.__fields__.values() for cls in settings))
    classes: Dict[Type[BaseSettings], List[ModelField]] = {cls: list(cls.__fields__.values()) for cls in settings}

    render_kwargs = {"heading_offset": heading_offset, "fields": fields, "classes": classes}

    env = Environment(
        loader=FileSystemLoader(templates + [TEMPLATES_FOLDER]),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["is_values_with_descriptions"] = is_values_with_descriptions
    render = get_template(env, output_format).render(**render_kwargs)

    if update_file is None:
        print(render)
        return

    with open(update_file, "r", encoding="utf-8") as file:
        content = file.read()

    with open(update_file, "w", encoding="utf-8") as file:
        if all(update_between):
            pattern = re.compile(f"({re.escape(update_between[0])}\n?).*(\n?{re.escape(update_between[1])})", re.DOTALL)

            if pattern.search(content) is None:
                secho(
                    f"Boundary marks '{update_between[0]}' and '{update_between[1]}' not found in '{update_file}'. "
                    f"Cannot update the content.",
                    fg=colors.RED,
                    err=True,
                )
                raise Abort()

            new_content = pattern.sub(f"\\1{render}\\2", content, count=1)
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
