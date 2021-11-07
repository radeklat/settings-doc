from pydantic import BaseSettings, Field


class EmptySettings(BaseSettings):
    var: str


class FullSettings(BaseSettings):
    var: str = Field(
        "some_value",
        description="use it like this",
        example="this is an example use",
        possible_values=["aaa", "bbb"],
    )


class RequiredSettings(BaseSettings):
    var: str = Field(..., description="use it like this")


class PossibleValuesNotIterableSettings(BaseSettings):
    var: str = Field(..., possible_values=123456)
