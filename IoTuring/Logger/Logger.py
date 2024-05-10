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
    """ Log filter for log target (console or file) """

    def __init__(self, target: str) -> None:
        self.target = target

    def filter(self, record) -> bool:
        if not getattr(record, "logtarget") or self.target in getattr(record, "logtarget"):
            return True
        else:
            return False


class LogLevelFilter(logging.Filter):
    """ Log filter for loglevel, for later file logging"""

    def __init__(self, loglevel: LogLevel) -> None:
        self.loglevel = loglevel

    def filter(self, record) -> bool:
        if int(self.loglevel) > int(record.levelno):
            return False
        else:
            return True


class LogMessage(LogLevelObject):

    def __init__(self, source: str, message, color: str = "", logtarget: str = "") -> None:

        self.source = source
        self.color = color

        self.msg = " ".join(self.MessageToList(message))

        self.extra = {"source": self.source,
                      "file_message": self.msg,
                      "console_message": self.GetConsoleMessage(self.MessageToList(message)),
                      "color_prefix": self.GetColors()["prefix"],
                      "color_suffix": self.GetColors()["suffix"],
                      "logtarget": logtarget
                      }

    def GetColors(self) -> dict:
        if TerminalDetection.CheckTerminalSupportsColors():
            return {"prefix": self.color, "suffix": Colors.reset}
        else:
            return {"prefix": "", "suffix": ""}

    def SetPrefixLength(self) -> None:
        default_source_len = next(
            (l for s, l in consts.LOG_PREFIX_LENGTHS.items() if s.startswith("source")))
        extra_len = max(len(self.source) - default_source_len, 0)
        self.console_prefix_length = Logger().console_prefix_length
        self.prefix_length = self.console_prefix_length + extra_len

    def GetConsoleMessage(self, messagelines: list[str]) -> str:

        if not TerminalDetection.CheckTerminalSupportsSize() or TerminalDetection.GetTerminalColumns() < consts.MIN_CONSOLE_WIDTH:
            return self.msg

        self.SetPrefixLength()

        if len(messagelines) == 1 \
                and TerminalDetection.CalculateNumberOfLines(len(messagelines[0]) + self.prefix_length) == 1:
            return messagelines[0]

        line_length = TerminalDetection.GetTerminalColumns() - \
            self.console_prefix_length

        final_lines = []

        if self.prefix_length > self.console_prefix_length:

            first_line_len = TerminalDetection.GetTerminalColumns() - \
                self.prefix_length
            final_lines.append(messagelines[0][:first_line_len])
            messagelines[0] = messagelines[0][first_line_len:]

        for l in messagelines:
            final_lines.extend([l[i:i+line_length]
                                for i in range(0, len(l), line_length)])

        line_prefix = "\n" + " " * self.console_prefix_length
        return line_prefix.join(final_lines)

    @staticmethod
    def MessageToList(message) -> list[str]:
        """Convert message to a nice list of strings

        Args:
            message (Any): The message

        Returns:
            list[str]: Formatted lines of the message as a list
        """
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

        return [l.strip() for l in lines]


class Logger(LogLevelObject, metaclass=Singleton):

    log_dir_path = ""
    file_handler = None
    console_prefix_length = 0

    def __init__(self) -> None:

        # Start root logger:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(10)

        # Init console logger handler:
        self.console_handler = logging.StreamHandler()
        self.SetupConsoleLogging()
        self.console_handler.addFilter(LogTargetFilter(self.LOGTARGET_CONSOLE))
        self.logger.addHandler(self.console_handler)

        # Init file logger buffer handler:
        self.memory_handler = logging.handlers.MemoryHandler(
            capacity=100, flushOnClose=False)
        self.logger.addHandler(self.memory_handler)

    def SetupConsoleLogging(self, loglevel: LogLevel = LogLevel(consts.DEFAULT_LOG_LEVEL), include_time: bool = True) -> None:
        self.console_handler.setFormatter(
            self.GetFormatter(self.LOGTARGET_CONSOLE, include_time))

        if OsD.GetEnv("IOTURING_LOG_LEVEL"):
            try:
                env_level = LogLevel(OsD.GetEnv("IOTURING_LOG_LEVEL"))
                self.console_handler.setLevel(int(env_level))
                return
            except UnknownLoglevelException:
                pass
        self.console_handler.setLevel(int(loglevel))

    def SetupFileLogging(self, enabled: bool, loglevel: LogLevel, log_dir_path: Path, early_init: bool) -> None:

        if enabled:
            if self.file_handler:
                self.UpdateFileLogging(loglevel, log_dir_path)
            else:
                self.StartFileLogging(loglevel, log_dir_path)
        else:
            if self.file_handler:
                self.logger.removeHandler(self.file_handler)
                self.file_handler.close()
                self.file_handler = None

        if not early_init:
            self.DisableFileLogBuffer()

    def StartFileLogging(self, loglevel: LogLevel, log_dir_path: Path) -> None:

        filepath = log_dir_path.joinpath(App.getName() + ".log")
        self.log_dir_path = log_dir_path

        self.file_handler = logging.handlers.RotatingFileHandler(
            filepath, backupCount=5)

        self.Log(self.LOG_DEBUG, "FileLogger", f"Started file logging: {filepath.absolute()}",
                 logtarget=self.LOGTARGET_CONSOLE)

        if filepath.exists():
            self.file_handler.doRollover()

        self.file_handler.setFormatter(self.GetFormatter(self.LOGTARGET_FILE))
        self.file_handler.addFilter(LogLevelFilter(loglevel))
        self.file_handler.addFilter(LogTargetFilter(self.LOGTARGET_FILE))
        self.file_handler.setLevel(int(loglevel))

        self.logger.addHandler(self.file_handler)

        self.memory_handler.setTarget(self.file_handler)
        self.memory_handler.flush()

    def UpdateFileLogging(self, loglevel: LogLevel, log_dir_path: Path) -> None:
        if not self.file_handler:
            raise Exception("File logger not initialized!")

        if log_dir_path.samefile(self.log_dir_path):
            if not self.file_handler.level == int(loglevel):

                # Update loglevel:
                old_filter = next(
                    (f for f in self.file_handler.filters if isinstance(f, LogLevelFilter)))
                self.file_handler.removeFilter(old_filter)

                self.file_handler.addFilter(LogLevelFilter(loglevel))
                self.file_handler.setLevel(int(loglevel))

        else:
            # Update path and loglevel
            self.logger.removeHandler(self.file_handler)
            self.StartFileLogging(loglevel, log_dir_path)

    def DisableFileLogBuffer(self) -> None:

        self.Log(self.LOG_DEBUG, "FileLogger", "File log buffer disabled",
                 logtarget=self.LOGTARGET_CONSOLE)

        if self.memory_handler:
            self.logger.removeHandler(self.memory_handler)
            self.memory_handler.close()

    def GetFormatter(self, logtarget: str, include_time: bool = True) -> logging.Formatter:

        prefix_lengths = consts.LOG_PREFIX_LENGTHS.copy()

        if not include_time:
            prefix_lengths.pop("asctime")

        prefix_strings = [f"{{{s}}}" for s in prefix_lengths]
        prefix_string = consts.LOG_PREFIX_ENDS[0] +\
            consts.LOG_PREFIX_SEPARATOR.join(prefix_strings) +\
            consts.LOG_PREFIX_ENDS[1]

        prefix_length = sum([len(s) for s in consts.LOG_PREFIX_ENDS]) + \
            len(consts.LOG_PREFIX_SEPARATOR) * (len(prefix_lengths) - 1) + \
            sum([l for l in prefix_lengths.values()])

        if logtarget == self.LOGTARGET_CONSOLE:
            fmt = "{color_prefix}" + prefix_string + \
                "{console_message}{color_suffix}"
            self.console_prefix_length = prefix_length
        elif logtarget == self.LOGTARGET_FILE:
            fmt = prefix_string + "{file_message}"
        else:
            raise Exception(f"Unknown logtarget: {logtarget}")

        return logging.Formatter(
            fmt=fmt,
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{"
        )

    def Log(self, loglevel: LogLevel, source: str, message, color: str = "", logtarget: str = "") -> None:

        log_message = LogMessage(
            source=source, message=message, color=color or loglevel.color, logtarget=logtarget)

        l = logging.getLogger(__name__).getChild(source)

        l.log(int(loglevel),
              msg=log_message.msg, extra=log_message.extra)
