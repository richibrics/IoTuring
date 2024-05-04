from __future__ import annotations
import logging
from IoTuring.Logger.Colors import Colors
from IoTuring.Exceptions.Exceptions import UnknownLoglevelException


class LogLevel:
    """ A loglevel with numeric and string values"""

    def __init__(self, level_const: str) -> None:

        self.string = level_const.upper()
        if self.string.startswith("LOG_"):
            self.string = self.string[4:]

        try:
            self.number = getattr(logging, self.string)
        except AttributeError:
            raise UnknownLoglevelException(level_const)

        if self.number == 30:
            self.color = Colors.yellow
        elif self.number > 30:
            self.color = Colors.red
        else:
            self.color = ""

    def __str__(self) -> str:
        return self.string

    def __int__(self) -> int:
        return self.number


class LogLevelObject:
    """ Base class for loglevel properties """

    LOG_DEBUG = LogLevel("DEBUG")
    LOG_INFO = LogLevel("INFO")
    LOG_WARNING = LogLevel("WARNING")
    LOG_ERROR = LogLevel("ERROR")
    LOG_CRITICAL = LogLevel("CRITICAL")

    LOG_FILE_ONLY = "file"
    LOG_CONSOLE_ONLY = "console"
    LOG_BOTH = LOG_FILE_ONLY + " " + LOG_CONSOLE_ONLY

    @classmethod
    def GetLoglevels(cls) -> list[LogLevel]:
        return [getattr(cls, l) for l in dir(cls) if isinstance(getattr(cls, l), LogLevel)]
