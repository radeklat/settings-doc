from pydantic import BaseSettings, Field


class SecondarySingleSettingsInModule(BaseSettings):
    logging_level: str = Field(..., description="SecondarySingleSettingsInModule")
