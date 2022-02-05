from typing import Iterable, List, Type

from pydantic import BaseSettings


def get_class_title(cls: Type[BaseSettings]) -> str:
    return cls.Config.title if getattr(getattr(cls, 'Config', None), 'title', None) else cls.__name__


def settings_doc_pre_render(render_kwargs: dict) -> dict:
    # Sort classes by their titles
    render_kwargs["titles"] = list(get_class_title(cls) for cls in render_kwargs["classes"])

    return render_kwargs
