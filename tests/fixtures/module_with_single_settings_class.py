from pydantic import Field
from pydantic_settings import BaseSettings


class SingleSettingsInModule(BaseSettings):
    logging_level: str = Field(..., description="SingleSettingsInModule")
