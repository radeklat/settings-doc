from __future__ import annotations

import sys
from enum import Enum, EnumMeta, IntEnum
from typing import Any, Callable
from typing import Iterable as IterableCollection
from typing import Literal

import click
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined


def _has_default_value(field: FieldInfo) -> bool:
    return field.default is not PydanticUndefined


def _is_values_with_descriptions(value: Any) -> bool:
    if not isinstance(value, IterableCollection):
        click.secho(f"`examples` must be iterable but `{value}` used.", fg="red")
        raise click.Abort()

    return all(list(map(lambda item: isinstance(item, list) and 2 >= len(item) >= 1, value)))


def _is_typing_literal(field: FieldInfo) -> bool:
    if sys.version_info < (3, 9) and field.annotation is not None and hasattr(field.annotation, "__origin__"):
        return field.annotation.__origin__ is Literal

    # The class doesn't exist in Python 3.8 and below
    return field.annotation.__class__.__name__ == "_LiteralGenericAlias"


def _fix_str_enum_value(value: Any) -> Any:
    """Fixes the value of an enum that subclasses `str`.

    In Python 3.10 and below, str + Enum can be used to create a StrEnum available in Python 3.11+.
    However, the value of the enum is not a string but an instance of the enum.
    """
    if (isinstance(value, str) and isinstance(value, Enum)) or isinstance(value, IntEnum):
        return value.value

    return value


def _is_enum(field: FieldInfo) -> bool:
    return isinstance(field.annotation, EnumMeta)


JINJA_ENV_GLOBALS: dict[str, Callable] = {
    "has_default_value": _has_default_value,
    "is_values_with_descriptions": _is_values_with_descriptions,
    "is_typing_literal": _is_typing_literal,
    "fix_str_enum_value": _fix_str_enum_value,
    "is_enum": _is_enum,
}
