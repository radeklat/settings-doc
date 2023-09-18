from pydantic import Field
from pydantic_settings import BaseSettings


class SecondarySingleSettingsInModule(BaseSettings):
    logging_level: str = Field(..., description="SecondarySingleSettingsInModule")
