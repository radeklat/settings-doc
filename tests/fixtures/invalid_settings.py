from pydantic import BaseSettings, Field


class PossibleValuesNotIterableSettings(BaseSettings):
    logging_level: str = Field(..., possible_values=123456)
