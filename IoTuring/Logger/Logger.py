from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from IoTuring.Logger.Colors import Colors
from IoTuring.Logger import consts
from IoTuring.Logger.LogLevel import LogLevelObject, LogLevel
from IoTuring.Exceptions.Exceptions import UnknownLoglevelException
from IoTuring.MyApp.SystemConsts import TerminalDetection
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.App import App


class Singleton(type):
    """ Metaclass for singleton classes """

    # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python/6798042#6798042

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__()
        return cls._instances[cls]


class LogTargetFilter(logging.Filter):
    def __init__(self, target: str) -> None:
        self.target = target

    def filter(self, record):
        if self.target in record.getMessage():
            return True
        else:
            return False


class LogLevelFilter(logging.Filter):
    def __init__(self, loglevel: LogLevel) -> None:
        self.loglevel = loglevel

    def filter(self, record):
        if int(self.loglevel) > int(record.levelno):
            return False
        else:
            return True


class Logger(LogLevelObject, metaclass=Singleton):

    prefix_length = 70

    console_formatter = logging.Formatter(
        fmt="{color_prefix}[ {asctime:s} | {levelname:^10s} | {source:^30s} | {console_message:s}{color_suffix}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        defaults={"color_prefix": "",
                  "color_suffix": ""
                  })

    file_formatter = logging.Formatter(
        fmt="[ {asctime:s} | {levelname:^10s} | {source:^30s} | {file_message:s}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{"
    )

    final_settings = False
    log_dir_path = ""
    file_handler = None

    def __init__(self) -> None:

        # Start root logger:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(10)

        # Init console logger handler:
        self.console_handler = logging.StreamHandler()
        self.SetConsoleLogLevel()
        self.console_handler.setFormatter(self.console_formatter)
        self.console_handler.addFilter(LogTargetFilter(self.LOG_CONSOLE_ONLY))
        self.logger.addHandler(self.console_handler)

        # Init file logger buffer handler:
        self.memory_handler = logging.handlers.MemoryHandler(capacity=100)
        self.logger.addHandler(self.memory_handler)

    def SetConsoleLogLevel(self, loglevel: LogLevel = LogLevel(consts.DEFAULT_LOG_LEVEL)) -> None:
        if OsD.GetEnv("IOTURING_LOG_LEVEL"):
            try:
                env_level = LogLevel(OsD.GetEnv("IOTURING_LOG_LEVEL"))
                self.console_handler.setLevel(int(env_level))
                return
            except UnknownLoglevelException:
                pass
        self.console_handler.setLevel(int(loglevel))

    def SetupFileLogging(self, enabled: bool, loglevel: LogLevel, log_dir_path: Path) -> None:

        if enabled:
            self.StartFileLogging(loglevel, log_dir_path)

        elif self.final_settings:
            self.DisableFileLogging()

        self.final_settings = True

    def StartFileLogging(self, loglevel: LogLevel, log_dir_path: Path) -> None:

        self.Log(self.LOG_DEBUG, "FileLogger", f"Started file logging: {log_dir_path.absolute()}",
                 logtarget=self.LOG_CONSOLE_ONLY)

        if self.file_handler:
            if log_dir_path.samefile(self.log_dir_path):
                self.file_handler.setLevel(int(loglevel))
                return
            else:
                self.logger.removeHandler(self.file_handler)

        filepath = log_dir_path.joinpath(App.getName() + ".log")
        self.log_dir_path = log_dir_path

        self.file_handler = logging.handlers.RotatingFileHandler(
            filepath, backupCount=5)

        if filepath.exists():
            self.file_handler.doRollover()

        self.file_handler.setFormatter(self.file_formatter)
        self.file_handler.addFilter(LogLevelFilter(loglevel))
        self.file_handler.addFilter(LogTargetFilter(self.LOG_FILE_ONLY))
        self.file_handler.setLevel(int(loglevel))

        self.logger.addHandler(self.file_handler)

        self.memory_handler.setTarget(self.file_handler)
        self.memory_handler.close()
        self.logger.removeHandler(self.memory_handler)

    def DisableFileLogging(self) -> None:

        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()

        if self.memory_handler:
            self.logger.removeHandler(self.memory_handler)
            self.memory_handler.close()

    def GetConsoleMessage(self, message, line_length) -> str:

        if isinstance(message, str) and len(message.splitlines()) == 1 and len(message) < line_length:
            return message.strip()

        final_lines = []

        for l in self.GetMessageAsList(message):
            short_lines = [l[i:i+line_length]
                           for i in range(0, len(l), line_length)]

            final_lines.extend(short_lines)

        line_prefix = "\n" + " " * self.prefix_length
        return line_prefix.join(final_lines)

    def GetFileMessage(self, message) -> str:
        return " ".join(self.GetMessageAsList(message))

    def GetMessageAsList(self, message) -> list[str]:
        if isinstance(message, list):
            messagelines = [str(i) for i in message]
        elif isinstance(message, dict):
            messagelines = [f"{k}: {v}" for k, v in message.items()]
        else:
            messagelines = [str(message)]

        lines = []

        # replace and split by newlines
        for m in messagelines:
            lines.extend(m.splitlines())

        return lines

    def Log(self, loglevel: LogLevel, source: str, message, color: str = "", logtarget: str = LogLevelObject.LOG_BOTH) -> None:

        available_length = TerminalDetection.GetTerminalColumns() - self.prefix_length

        extra = {"source": source,
                 "file_message": self.GetFileMessage(message),
                 "console_message": self.GetConsoleMessage(message, available_length)
                 }

        if TerminalDetection.CheckTerminalSupportsColors():

            if color or loglevel.color:
                extra["color_prefix"] = color or loglevel.color
                extra["color_suffix"] = Colors.reset

        l = logging.getLogger(__name__).getChild(source)

        l.log(int(loglevel), msg=logtarget, extra=extra)
