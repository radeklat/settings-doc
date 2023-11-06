from pydantic import Field
from pydantic_settings import BaseSettings


class ExamplesNotIterableSettings(BaseSettings):
    logging_level: str = Field(..., json_schema_extra={"examples": 123456})
