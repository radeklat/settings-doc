from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

SETTINGS_ATTR = "logging_level"
SETTINGS_MARKDOWN_FIRST_LINE = f"# `{SETTINGS_ATTR}`\n"


class EmptySettings(BaseSettings):
    logging_level: str


class FullSettings(BaseSettings):
    logging_level: str = Field(
        "some_value",
        description="use FullSettings like this",
        examples=["aaa", "bbb"],
    )


class LiteralSettings(BaseSettings):
    logging_level: Literal["debug", "info"]


class RequiredSettings(BaseSettings):
    logging_level: str = Field(..., description="RequiredSettings")


class MultipleSettings(BaseSettings):
    username: str
    password: str
