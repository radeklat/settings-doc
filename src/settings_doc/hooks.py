from functools import lru_cache
from itertools import chain
from pathlib import Path
from types import ModuleType
from typing import Iterable, Tuple, Callable, Set, Any, List

from click import BadParameter

from settings_doc import importing

HOOKS_PREFIX = "settings_doc_"

HOOK_INITIALIZE_ENVIRONMENT = "initialize_environment"
HOOK_PRE_RENDER = "pre_render"

VALID_HOOKS = {HOOK_INITIALIZE_ENVIRONMENT, HOOK_PRE_RENDER}


def get_hook_type_from_name(name: str) -> str:
    return name[len(HOOKS_PREFIX):]


def is_a_hook(name: str, member: Any) -> bool:
    return name.startswith(HOOKS_PREFIX) and callable(member)


@lru_cache()
def load_hooks_from_module(module: ModuleType) -> Iterable[Tuple[str, Callable]]:
    collected: Set[Any] = set()
    hooks: List[Tuple[str, Callable]] = []

    for name, member in vars(module).items():
        if is_a_hook(name, member) and member not in collected:
            collected.add(member)
            hook_type = get_hook_type_from_name(name)
            if hook_type not in VALID_HOOKS:
                raise BadParameter(f"{name} is not a valid hook in file: {module.__file__}")
            hooks.append((hook_type, member))

    if not hooks:
        raise BadParameter(f"No hooks were found in file: {module.__file__}")

    return hooks


@lru_cache()
def load_hooks_from_files(files: Tuple[Path, ...]) -> Iterable[Tuple[str, Callable]]:
    modules = importing.import_module_from_files(tuple(files))

    loaded_hooks = list(chain.from_iterable(load_hooks_from_module(module) for module in modules))

    return loaded_hooks


def hooks_path_callback(value: List[Path]) -> List[Path]:
    load_hooks_from_files(tuple(value))
    return value
