import importlib
from functools import lru_cache
from inspect import isclass
from typing import Dict, List, Tuple, Type

from click import BadParameter, secho
from pydantic_settings import BaseSettings
from typer import colors

_MODULE_ERROR_MSG = "No `pydantic.BaseSettings` subclasses found in module '{module_path}'."
_RELATIVE_IMPORT_ERROR_MSG = "Relative imports are not supported."


@lru_cache
def import_module_path(module_paths: Tuple[str, ...]) -> Dict[Type[BaseSettings], None]:
    if not module_paths:
        return {}

    settings: Dict[Type[BaseSettings], None] = {}

    for module_path in module_paths:
        try:
            module = importlib.import_module(module_path)
        except (ModuleNotFoundError, TypeError) as exc:
            cause = str(exc)
            if isinstance(exc, TypeError) and "relative import" in cause:
                cause = _RELATIVE_IMPORT_ERROR_MSG
            raise BadParameter(f"Cannot read the module: {cause}") from exc

        new_classes: Dict[Type[BaseSettings], None] = {
            obj: None
            for obj in vars(module).values()
            if isclass(obj) and issubclass(obj, BaseSettings) and obj.__module__.startswith(module_path)
        }

        if not new_classes:
            if len(module_paths) > 1:
                secho(_MODULE_ERROR_MSG.format(module_path=module_path), fg=colors.YELLOW, err=True)
        else:
            settings.update(new_classes)

    if not settings:
        raise BadParameter(
            _MODULE_ERROR_MSG.format(module_path=module_paths[0])
            if len(module_paths) == 1
            else "No `pydantic.BaseSettings` subclasses found in any of the modules."
        )

    return settings


@lru_cache
def import_class_path(class_paths: Tuple[str, ...]) -> Dict[Type[BaseSettings], None]:
    settings: Dict[Type[BaseSettings], None] = {}

    for class_path in class_paths:
        module, class_name = class_path.rsplit(".", maxsplit=1)
        try:
            new_class = getattr(importlib.import_module(module), class_name)
        except (AttributeError, ModuleNotFoundError, TypeError) as exc:
            cause = str(exc)
            if isinstance(exc, TypeError) and "relative import" in cause:
                cause = _RELATIVE_IMPORT_ERROR_MSG
            raise BadParameter(f"Cannot read the settings class: {cause}") from exc

        if not isclass(new_class):
            raise BadParameter(f"Target '{class_name}' in module '{module}' is not a class.")

        if not issubclass(new_class, BaseSettings):
            raise BadParameter(f"Target class must be a subclass of BaseSettings but '{new_class.__name__}' found.")

        settings[new_class] = None

    return settings


def module_path_callback(value: List[str]) -> List[str]:
    import_module_path(tuple(value))
    return value


def class_path_callback(value: List[str]) -> List[str]:
    import_class_path(tuple(value))
    return value
