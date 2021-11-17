from pydantic import BaseSettings


class SingleSettingsInModule(BaseSettings):
    logging_level: str
