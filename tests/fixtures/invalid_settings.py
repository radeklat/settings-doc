from pydantic import Field
from pydantic_settings import BaseSettings


class ExamplesNotIterableSettings(BaseSettings):
    logging_level: str = Field(..., examples=123456)  # type: ignore[arg-type]
