import itertools
import logging
import re
import shutil
import sys
from collections.abc import Iterable as IterableCollection
from enum import Enum, auto
from os import listdir
from pathlib import Path
from typing import Any, Dict, Final, Iterator, List, Literal, Optional, Set, Tuple, Type

from click import Abort, secho
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings
from typer import Option, Typer, colors

from settings_doc import importing

app = Typer()


TEMPLATES_FOLDER: Final[Path] = Path(__file__).parent / "templates"
LOGGER = logging.getLogger(__name__)


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
        secho(f"`examples` must be iterable but `{value}` used.", fg=colors.RED)
        raise Abort()

    return all(list(map(lambda item: isinstance(item, list) and 2 >= len(item) >= 1, value)))


def has_default_value(field: FieldInfo) -> bool:
    return field.default is not PydanticUndefined


def get_template(env: Environment, output_format: OutputFormat) -> Template:
    return env.get_template(f"{output_format.value}.jinja")


def is_typing_literal(field: FieldInfo) -> bool:
    if sys.version_info < (3, 9) and field.annotation is not None and hasattr(field.annotation, "__origin__"):
        return field.annotation.__origin__ is Literal

    # The class doesn't exist in Python 3.8 and below
    return field.annotation.__class__.__name__ == "_LiteralGenericAlias"


def _model_fields_recursive(
    cls: Type[BaseSettings], prefix: str, env_nested_delimiter: Optional[str]
) -> Iterator[Tuple[str, FieldInfo]]:
    for field_name, model_field in cls.model_fields.items():
        if model_field.validation_alias is not None:
            if isinstance(model_field.validation_alias, str):
                yield model_field.validation_alias, model_field
            else:
                LOGGER.error(f"Unsupported validation alias type '{type(model_field.validation_alias)}'.")
        elif (
            model_field.annotation is not None
            and hasattr(model_field.annotation, "model_fields")
            and env_nested_delimiter is not None
        ):
            # There are nested fields and they can be joined by a delimiter. Generate variable names recursively.
            yield from _model_fields_recursive(
                model_field.annotation,
                prefix + field_name + env_nested_delimiter,
                env_nested_delimiter,
            )
        else:
            yield prefix + field_name, model_field


def _model_fields(cls: Type[BaseSettings]) -> Iterator[Tuple[str, FieldInfo]]:
    yield from _model_fields_recursive(cls, cls.model_config["env_prefix"], cls.model_config["env_nested_delimiter"])


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

    fields = itertools.chain.from_iterable(_model_fields(cls) for cls in settings)
    classes: Dict[Type[BaseSettings], List[FieldInfo]] = {cls: list(cls.model_fields.values()) for cls in settings}

    render_kwargs = {"heading_offset": heading_offset, "fields": fields, "classes": classes}

    env = Environment(
        loader=FileSystemLoader(templates + [TEMPLATES_FOLDER]),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["is_values_with_descriptions"] = is_values_with_descriptions
    env.globals["has_default_value"] = has_default_value
    env.globals["is_typing_literal"] = is_typing_literal
    render = get_template(env, output_format).render(**render_kwargs)

    if update_file is None:
        print(render)
        return

    with open(update_file, encoding="utf-8") as file:
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
