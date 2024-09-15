from __future__ import annotations

import importlib
from functools import lru_cache
from inspect import isclass

import click
from pydantic_settings import BaseSettings

_MODULE_ERROR_MSG = "No `pydantic.BaseSettings` subclasses found in module '{module_path}'."
_RELATIVE_IMPORT_ERROR_MSG = "Relative imports are not supported."


@lru_cache
def import_module_path(module_paths: tuple[str, ...]) -> dict[type[BaseSettings], None]:
    if not module_paths:
        return {}

    settings: dict[type[BaseSettings], None] = {}

    for module_path in module_paths:
        try:
            module = importlib.import_module(module_path)
        except (ModuleNotFoundError, TypeError) as exc:
            cause = str(exc)
            if isinstance(exc, TypeError) and "relative import" in cause:
                cause = _RELATIVE_IMPORT_ERROR_MSG
            raise click.BadParameter(f"Cannot read the module: {cause}") from exc

        new_classes: dict[type[BaseSettings], None] = {
            obj: None
            for obj in vars(module).values()
            if isclass(obj) and issubclass(obj, BaseSettings) and obj.__module__.startswith(module_path)
        }

        if not new_classes:
            if len(module_paths) > 1:
                click.secho(_MODULE_ERROR_MSG.format(module_path=module_path), fg="yellow", err=True)
        else:
            settings.update(new_classes)

    if not settings:
        raise click.BadParameter(
            _MODULE_ERROR_MSG.format(module_path=module_paths[0])
            if len(module_paths) == 1
            else "No `pydantic.BaseSettings` subclasses found in any of the modules."
        )

    return settings


@lru_cache
def import_class_path(class_paths: tuple[str, ...]) -> dict[type[BaseSettings], None]:
    settings: dict[type[BaseSettings], None] = {}

    for class_path in class_paths:
        module, class_name = class_path.rsplit(".", maxsplit=1)
        try:
            new_class = getattr(importlib.import_module(module), class_name)
        except (AttributeError, ModuleNotFoundError, TypeError) as exc:
            cause = str(exc)
            if isinstance(exc, TypeError) and "relative import" in cause:
                cause = _RELATIVE_IMPORT_ERROR_MSG
            raise click.BadParameter(f"Cannot read the settings class: {cause}") from exc

        if not isclass(new_class):
            raise click.BadParameter(f"Target '{class_name}' in module '{module}' is not a class.")

        if not issubclass(new_class, BaseSettings):
            raise click.BadParameter(
                f"Target class must be a subclass of BaseSettings but '{new_class.__name__}' found."
            )

        settings[new_class] = None

    return settings


def module_path_callback(ctx: click.Context, param: click.Parameter, value: list[str]) -> list[str]:
    del ctx, param
    import_module_path(tuple(value))
    return value


def class_path_callback(ctx: click.Context, param: click.Parameter, value: list[str]) -> list[str]:
    del ctx, param
    import_class_path(tuple(value))
    return value
