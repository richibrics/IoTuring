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


class Logger(LogLevelObject, metaclass=Singleton):

    final_settings = False
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

    def SetupFileLogging(self, enabled: bool, loglevel: LogLevel, log_dir_path: Path) -> None:

        if enabled:
            self.StartFileLogging(loglevel, log_dir_path)

        if self.final_settings:
            self.FinalizeFileLogging(enabled)

        self.final_settings = True

    def StartFileLogging(self, loglevel: LogLevel, log_dir_path: Path) -> None:

        if self.file_handler:
            if log_dir_path.samefile(self.log_dir_path):
                if not self.file_handler.level == int(loglevel):

                    old_filter = next(
                        (f for f in self.file_handler.filters if isinstance(f, LogLevelFilter)))
                    self.file_handler.removeFilter(old_filter)

                    self.file_handler.addFilter(LogLevelFilter(loglevel))
                    self.file_handler.setLevel(int(loglevel))

                return
            else:
                self.logger.removeHandler(self.file_handler)

        else:
            self.Log(self.LOG_DEBUG, "FileLogger", f"Started file logging: {log_dir_path.absolute()}",
                     logtarget=self.LOGTARGET_CONSOLE)

        filepath = log_dir_path.joinpath(App.getName() + ".log")
        self.log_dir_path = log_dir_path

        self.file_handler = logging.handlers.RotatingFileHandler(
            filepath, backupCount=5)

        if filepath.exists():
            self.file_handler.doRollover()

        self.file_handler.setFormatter(self.GetFormatter(self.LOGTARGET_FILE))
        self.file_handler.addFilter(LogLevelFilter(loglevel))
        self.file_handler.addFilter(LogTargetFilter(self.LOGTARGET_FILE))
        self.file_handler.setLevel(int(loglevel))

        self.logger.addHandler(self.file_handler)

        self.memory_handler.setTarget(self.file_handler)
        self.memory_handler.flush()

    def FinalizeFileLogging(self, enabled: bool) -> None:

        if not enabled and self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()

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

    def GetConsoleMessage(self, source: str, message) -> str:

        if isinstance(message, str) \
            and len(message.splitlines()) == 1 \
                and len(message) + self.GetPrefixLength(source) < TerminalDetection.GetTerminalColumns():
            return message.strip()

        line_length = TerminalDetection.GetTerminalColumns() - \
            self.GetPrefixLength()

        final_lines = []
        messagelines = self.GetMessageAsList(message)

        if self.GetPrefixLength(source) > self.GetPrefixLength():
            first_line_len = TerminalDetection.GetTerminalColumns() - \
                self.GetPrefixLength(source)
            final_lines.append(messagelines[0][:first_line_len])
            messagelines[0] = messagelines[0][first_line_len:]

        for l in messagelines:
            final_lines.extend([l[i:i+line_length]
                                for i in range(0, len(l), line_length)])

        line_prefix = "\n" + " " * self.GetPrefixLength()
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

    def GetPrefixLength(self, source: str = "") -> int:
        default_source_len = next(
            (l for s, l in consts.LOG_PREFIX_LENGTHS.items() if s.startswith("source")))
        extra_len = max(len(source) - default_source_len, 0)
        return self.console_prefix_length + extra_len

    def Log(self, loglevel: LogLevel, source: str, message, color: str = "", logtarget: str = "") -> None:

        extra = {"source": source,
                 "file_message": self.GetFileMessage(message),
                 "color_prefix": "",
                 "color_suffix": "",
                 "logtarget": logtarget
                 }

        if TerminalDetection.CheckTerminalSupportsSize() and TerminalDetection.GetTerminalColumns() > consts.MIN_CONSOLE_WIDTH:
            extra["console_message"] = self.GetConsoleMessage(source, message)
        else:
            extra["console_message"] = extra["file_message"]

        if TerminalDetection.CheckTerminalSupportsColors():

            if color or loglevel.color:
                extra["color_prefix"] = color or loglevel.color
                extra["color_suffix"] = Colors.reset

        l = logging.getLogger(__name__).getChild(source)

        l.log(int(loglevel), msg=message, extra=extra)
