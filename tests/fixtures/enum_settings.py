import enum
import sys
from typing import Type

import pytest
from pydantic_settings import BaseSettings


@pytest.fixture(scope="session")
def str_enum_settings() -> Type[BaseSettings]:
    if sys.version_info < (3, 11):
        StrEnum = enum.Enum  # pylint: disable=invalid-name
        pytest.fail("StrEnum is not available in Python 3.10 and below")
    else:
        from enum import StrEnum  # pylint: disable=import-outside-toplevel

    class LoggingLevelEnum(StrEnum):  # type: ignore[valid-type, misc, unused-ignore]
        DEBUG = "debug"
        INFO = "info"

    class StrEnumSettings(BaseSettings):
        logging_level: LoggingLevelEnum = LoggingLevelEnum.DEBUG

    return StrEnumSettings


@pytest.fixture(scope="session")
def str_enum_subclass_settings() -> Type[BaseSettings]:
    class LoggingLevelEnum(str, enum.Enum):
        DEBUG = "debug"
        INFO = "info"

    class StrEnumSubclassSettings(BaseSettings):
        logging_level: LoggingLevelEnum = LoggingLevelEnum.DEBUG

    return StrEnumSubclassSettings


@pytest.fixture(scope="session")
def int_enum_settings() -> Type[BaseSettings]:
    class LoggingLevelEnum(enum.IntEnum):
        DEBUG = 10
        INFO = 20

    class IntEnumSettings(BaseSettings):
        logging_level: LoggingLevelEnum = LoggingLevelEnum.DEBUG

    return IntEnumSettings
