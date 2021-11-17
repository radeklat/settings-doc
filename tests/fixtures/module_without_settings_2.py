# This is a module where no `pydantic.BaseSettings` subclass is present.
from dataclasses import dataclass


@dataclass
class NotSettings:
    logging_level: str
