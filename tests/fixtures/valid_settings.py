from typing import Literal

from pydantic import AliasChoices, AliasPath, Field
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


class ValidationAliasSettings(BaseSettings):
    logging_level_alias: str = Field(..., validation_alias="logging_level")


class ValidationAliasPathSettings(BaseSettings):
    logging_level: str = Field(..., validation_alias=AliasPath("logging_level", 0))


class ValidationAliasChoicesSettings(BaseSettings):
    logging_level: str = Field(..., validation_alias=AliasChoices("logging", "level"))
