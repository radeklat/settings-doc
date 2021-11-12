from pydantic import BaseSettings, Field

SETTINGS_ATTR = "logging_level"
SETTINGS_MARKDOWN_FIRST_LINE = f"# `{SETTINGS_ATTR}`\n"


class EmptySettings(BaseSettings):
    logging_level: str


class FullSettings(BaseSettings):
    logging_level: str = Field(
        "some_value",
        description="use it like this",
        example="this is an example use",
        possible_values=["aaa", "bbb"],
    )


class RequiredSettings(BaseSettings):
    logging_level: str = Field(..., description="use it like this")


class PossibleValuesNotIterableSettings(BaseSettings):
    logging_level: str = Field(..., possible_values=123456)
