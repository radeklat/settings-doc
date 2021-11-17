from pydantic import BaseSettings, Field


class SingleSettingsInModule(BaseSettings):
    logging_level: str = Field(..., description="SingleSettingsInModule")
