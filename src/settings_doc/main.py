from __future__ import annotations

import itertools
import logging
import re
import shutil
from enum import Enum, auto
from inspect import isclass
from os import listdir
from pathlib import Path
from typing import Final, Iterator

import click
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings

from settings_doc import importing
from settings_doc.template_functions import JINJA_ENV_GLOBALS

TEMPLATES_FOLDER: Final[Path] = Path(__file__).parent / "templates"
LOGGER = logging.getLogger(__name__)


@click.group()
def app():
    pass


class OutputFormat(Enum):
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):  # pylint: disable=no-self-argument
        del start, count, last_values
        return name.lower()  # pylint: disable=no-member

    DOTENV = auto()
    MARKDOWN = auto()
    DEBUG = auto()


def get_template(env: Environment, output_format: OutputFormat) -> Template:
    return env.get_template(f"{output_format.value}.jinja")


def _model_fields_recursive(
    cls: type[BaseModel], prefix: str, env_nested_delimiter: str | None
) -> Iterator[tuple[str, FieldInfo]]:
    for field_name, model_field in cls.model_fields.items():
        if model_field.validation_alias is not None:
            if isinstance(model_field.validation_alias, str):
                yield model_field.validation_alias, model_field
            else:
                LOGGER.error(f"Unsupported validation alias type '{type(model_field.validation_alias)}'.")
        elif isclass(model_field.annotation) and issubclass(model_field.annotation, BaseModel):
            # There are nested fields and they can be joined by a delimiter. Generate variable names recursively.
            if issubclass(model_field.annotation, BaseSettings):
                yield from _model_fields(model_field.annotation)
            else:  # BaseModel
                yield from _model_fields_recursive(
                    model_field.annotation,
                    prefix + field_name + (env_nested_delimiter or ""),
                    env_nested_delimiter or "",
                )
        else:
            yield prefix + field_name, model_field


def _model_fields(cls: type[BaseSettings]) -> Iterator[tuple[str, FieldInfo]]:
    yield from _model_fields_recursive(cls, cls.model_config["env_prefix"], cls.model_config["env_nested_delimiter"])


def render(
    output_format: OutputFormat,
    module_path: tuple[str, ...] | None = None,
    class_path: tuple[str, ...] | None = None,
    heading_offset: int = 0,
    templates: tuple[Path, ...] | None = None,
) -> str:
    """Render the settings documentation."""
    if not class_path and not module_path:
        raise ValueError("No sources of data were specified.")

    if module_path is None:
        module_path = tuple()

    if class_path is None:
        class_path = tuple()

    if templates is None:
        templates = tuple()

    settings: dict[type[BaseSettings], None] = importing.import_class_path(class_path)
    settings.update(importing.import_module_path(module_path))

    if not settings:
        raise ValueError("No sources of data were found.")

    fields = itertools.chain.from_iterable(_model_fields(cls) for cls in settings)
    classes: dict[type[BaseSettings], list[FieldInfo]] = {cls: list(cls.model_fields.values()) for cls in settings}

    env = Environment(
        loader=FileSystemLoader(templates + (TEMPLATES_FOLDER,)),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals.update(JINJA_ENV_GLOBALS)

    return get_template(env, output_format).render(
        heading_offset=heading_offset,
        fields=fields,
        classes=classes,
    )


@app.command()
@click.option(
    "--module",
    "-m",
    "module_path",
    callback=importing.module_path_callback,
    multiple=True,
    default=None,
    help="Period-separated import path to a module that contains one or more subclasses"
    "of `pydantic.BaseSettings`. All such sub-classes will be used to generate the output. "
    "If that is undesirable, use the `--class` option to specify classes manually. "
    "Must be importable from current working directory. Setting PYTHONPATH appropriately "
    "may be required.",
)
@click.option(
    "--class",
    "-c",
    "class_path",
    multiple=True,
    default=None,
    callback=importing.class_path_callback,
    help="Period-separated import path to a subclass of `pydantic.BaseSettings`. "
    "Must be importable from current working directory. Use `--module` instead to auto-discover "
    "all such subclasses in a module. Setting PYTHONPATH appropriately may be required.",
)
@click.option(
    "--output-format",
    "-f",
    required=True,
    type=click.Choice([_.value for _ in OutputFormat.__members__.values()]),
    callback=lambda ctx, param, value: None if value is None else OutputFormat[value.upper()],
)
@click.option(
    "--heading-offset",
    type=int,
    default=0,
    callback=lambda ctx, param, value: (
        value if value >= 0 else click.BadParameter("Value must be greater than or equal to 0.")
    ),
    help="How nested should be the top level heading generated.",
)
@click.option(
    "--update",
    "-u",
    "update_file",
    default=None,
    type=click.Path(exists=True, writable=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Overwrite given file instead of writing to STDOUT. An error is raised if the "
    "file doesn't exist or is not writable. Combine this flag with the '--between' "
    "flag to update only a section of a file. ",
)
@click.option(
    "--between",
    "update_between",
    default=(None, None),
    type=(str, str),
    help="Update file given by '--update' between these two strings. New line after "
    "the start mark/before the end mark is considered part of the pattern (if present). "
    "Without the '--update' flag, this has no effect. ",
)
@click.option(
    "--templates",
    default=None,
    type=click.Path(exists=True, writable=True, file_okay=False, dir_okay=True, resolve_path=True),
    multiple=True,
    help="Folder to use when looking up templates for generating output. Can be used "
    "more than once, in a priority order. Built-in templates will be used last if no "
    "matches found.",
)
def generate(
    module_path: tuple[str, ...] | None,
    class_path: tuple[str, ...] | None,
    output_format: OutputFormat,
    heading_offset: int,
    update_file: Path | None,
    update_between: tuple[str | None, str | None],
    templates: tuple[Path, ...] | None,
):
    """Formats `pydantic.BaseSettings` into various formats. By default, the output is to STDOUT."""
    try:
        rendered_doc = render(output_format, module_path, class_path, heading_offset, templates)
    except ValueError as exc:
        click.secho(str(exc) + " Check the '--module' or '--class' options.", fg="red", err=True)
        raise click.Abort() from exc

    if update_file is None:
        print(rendered_doc)
        return

    with open(update_file, encoding="utf-8") as file:
        content = file.read()

    with open(update_file, "w", encoding="utf-8") as file:
        if update_between[0] and update_between[1]:
            pattern = re.compile(f"({re.escape(update_between[0])}\n?).*(\n?{re.escape(update_between[1])})", re.DOTALL)

            if pattern.search(content) is None:
                click.secho(
                    f"Boundary marks '{update_between[0]}' and '{update_between[1]}' not found in '{update_file}'. "
                    f"Cannot update the content.",
                    fg="red",
                    err=True,
                )
                raise click.Abort()

            new_content = pattern.sub(f"\\1{rendered_doc}\\2", content, count=1)
        else:
            new_content = rendered_doc

        file.write(new_content)


@app.command("templates")
@click.option(
    "--copy-to",
    type=click.Path(exists=True, writable=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Output folder. Any existing templates with the same names with be overwritten.",
)
def manipulate_templates(copy_to: Path):
    """Copies built-in Jinja2 templates into a folder for modifying."""
    for file in listdir(TEMPLATES_FOLDER):
        shutil.copy2(TEMPLATES_FOLDER / file, copy_to)


if __name__ == "__main__":
    app()
