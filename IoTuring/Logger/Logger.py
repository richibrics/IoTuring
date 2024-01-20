from __future__ import annotations

from datetime import datetime
import json
import threading
from pathlib import Path


from IoTuring.MyApp.App import App
from IoTuring.Logger import consts
from IoTuring.Logger.LogLevel import LogLevelObject, LogLevel
from IoTuring.Logger.Colors import Colors
from IoTuring.Exceptions.Exceptions import UnknownLoglevelException
from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import TerminalDetection as TD

# macOS dep (in PyObjC)
try:
    from AppKit import *  # type:ignore
    from Foundation import *  # type:ignore
    macos_support = True
except:
    macos_support = False


CONFIG_KEY_CONSOLE_LOG_LEVEL = "console_log_level"
CONFIG_KEY_FILE_LOG_LEVEL = "file_log_level"
CONFIG_KEY_FILE_LOG_ENABLED = "file_log_enabled"
CONFIG_KEY_FILE_LOG_PATH = "file_log_path"


LogLevelChoices = [{"name": l["string"], "value": l["const"]}
                   for l in consts.LOG_LEVELS]


class Singleton(type):
    """ Metaclass for singleton classes """

    # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python/6798042#6798042

    _instances = {}

    def __call__(cls):  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__()
        return cls._instances[cls]


class Logger(LogLevelObject, ConfiguratorObject, metaclass=Singleton):
    NAME = "Logger"

    startupTimeString = datetime.now().strftime(
        consts.LOG_FILENAME_FORMAT).replace(":", "_")

    terminalSupportsColors = TD.CheckTerminalSupportsColors()

    # Logger starts before configurator
    configurations = None

    # Default log levels:
    console_log_level = LogLevel(consts.DEFAULT_LOG_LEVEL)
    file_log_level = LogLevel(consts.DEFAULT_LOG_LEVEL)

    # File logs stored here, before configurator loaded.
    file_log_buffer = []

    file_log_enabled = None
    file_log_filename = None
    file_log_descriptor = None
    lock = None

    def __init__(self) -> None:

        self.SetConsoleLogLevel()

        diag_strings = [
            "Logger Init",
            f"Console Loglevel: {str(self.console_log_level)}",
            f"File Loglevel: {str(self.file_log_level)}"
        ]
        if self.configurations:
            diag_strings.extend([
                "Configurations:",
                self.configurations.ToDict()])
        else:
            diag_strings.append("Config not loaded yet")

        self.Log(self.LOG_DEVELOPMENT, "Logger", diag_strings)

        


        if self.configurations:

            try:
                # set up and start file logging:
                if self.GetTrueOrFalseFromConfigurations(CONFIG_KEY_FILE_LOG_ENABLED):

                    # Update file log level:
                    new_file_loglevel = self.SanitizeLoglevel(self.GetFromConfigurations(CONFIG_KEY_FILE_LOG_LEVEL))
                    if new_file_loglevel:
                        self.file_log_level = new_file_loglevel

                    self.SetupFileLogging()

                    self.WriteFileLogBuffer()

                    self.file_log_enabled = True
                else:
                    self.DisableFileLogging()
            except:

                self.DisableFileLogging()

    def SetConsoleLogLevel(self):
        new_loglevel = None
        # Override log level from envvar:
        if OsD.GetEnv("IOTURING_LOG_LEVEL"):
            new_loglevel = self.SanitizeLoglevel(OsD.GetEnv("IOTURING_LOG_LEVEL"))

        # Read from config:
        if not new_loglevel and self.configurations:
            new_loglevel = self.SanitizeLoglevel(
                self.GetFromConfigurations(CONFIG_KEY_CONSOLE_LOG_LEVEL))

        if new_loglevel:
            self.console_log_level = new_loglevel
            self.Log(self.LOG_DEBUG, "Logger",
                     f"Set Console Loglevel to: {str(self.console_log_level)}")
        else:
            self.Log(self.LOG_DEBUG, "Logger",
                     f"Console Loglevel not changed.")

    def SanitizeLoglevel(self, loglevel_string) -> LogLevel | None:
        try:
            l = LogLevel(str(loglevel_string))
            return l
        except UnknownLoglevelException as e:
            self.Log(self.LOG_WARNING, "Logger",
                     f"Unknown Loglevel: {e.loglevel}")
            return None

    def SetupFileLogging(self) -> None:
        log_dir_path = Path(
            self.GetFromConfigurations(CONFIG_KEY_FILE_LOG_PATH))
        if not log_dir_path.exists():
            log_dir_path.mkdir(parents=True)

        self.file_log_filename = log_dir_path.joinpath(self.startupTimeString)

        self.file_log_descriptor = \
            open(self.file_log_filename, "a", encoding="utf-8")

        self.lock = threading.Lock()

        self.Log(self.LOG_DEBUG, "Logger",
                     f"File Log setup finished.")


    def WriteFileLogBuffer(self):
        while self.file_log_buffer:
            line = self.file_log_buffer[0]
            self.WriteFileLogLine(line["string"], line["loglevel"])
            del self.file_log_buffer[0]

    def DisableFileLogging(self) -> None:
        self.file_log_enabled = False
        self.file_log_buffer = []
        self.CloseFile()
        self.Log(self.LOG_DEBUG, "Logger",
                     f"File logging disabled.")

    def GetMessageDatetimeString(self) -> str:
        now = datetime.now()
        return now.strftime(consts.MESSAGE_DATETIME_FORMAT)

    # LOG

    def Log(self, loglevel: LogLevel, source: str, message, **kwargs) -> None:
        if type(message) == dict:
            self.LogDict(loglevel, source, message, **kwargs)
            return  # Log dict will call this function so I don't need to go down at the moment
        elif type(message) == list:
            self.LogList(loglevel, source, message, **kwargs)
            return  # Log list will call this function so I don't need to go down at the moment

        message = str(message)
        # Call this function for each line of the message if there are more than one line.
        messageLines = message.split("\n")
        if len(messageLines) > 1:
            for line in messageLines:
                self.Log(loglevel, source, line, **kwargs)
            return  # Stop the function then because I've already called this function from each line so I don't have to go down here

        prestring = f"[ {self.GetMessageDatetimeString()} | {str(loglevel).center(consts.STRINGS_LENGTH[0])} | " \
            + f"{source.center(consts.STRINGS_LENGTH[1])}]{consts.PRESTRING_MESSAGE_SEPARATOR_LEN*' '}"  # justify

        # Manage string to print in more lines if it's too long
        while len(message) > 0:
            string = prestring+message[:consts.MESSAGE_WIDTH]
            # Cut for next iteration if message is longer than a line
            message = message[consts.MESSAGE_WIDTH:]
            # then I add the dash to the row
            if (len(message) > 0 and string[-1] != " " and string[-1] != "." and string[-1] != ","):
                string = string + '-'  # Print new line indicator if I will go down in the next iteration
            self.PrintAndSave(string, loglevel, **kwargs)
            # -1 + space cause if the char in the prestring isn't a space, it will be directly attached to my message without a space

            prestring = (len(prestring)-consts.PRESTRING_MESSAGE_SEPARATOR_LEN) * \
                consts.LONG_MESSAGE_PRESTRING_CHAR+consts.PRESTRING_MESSAGE_SEPARATOR_LEN*' '

    def LogDict(self, loglevel, source, message_dict: dict, **kwargs):
        try:
            string = json.dumps(message_dict, indent=4, sort_keys=False,
                                default=lambda o: '<not serializable>')
            lines = string.splitlines()
            for line in lines:
                self.Log(loglevel, source, "> "+line, **kwargs)
        except Exception as e:
            self.Log(self.LOG_ERROR, source,
                     "Can't print dictionary content", **kwargs)

    def LogList(self, loglevel, source, message_list: list, **kwargs):
        try:
            for index, item in enumerate(message_list):
                if type(item) == dict or type(item) == list:
                    self.Log(loglevel, source, "Item #"+str(index), **kwargs)
                    self.Log(loglevel, source, item, **kwargs)
                else:
                    self.Log(loglevel, source,
                             f"{str(index)}: {str(item)}", **kwargs)

        except:
            self.Log(self.LOG_ERROR, source,
                     "Can't print dictionary content", **kwargs)

    # Both print and save to file
    def PrintAndSave(self, string: str, loglevel: LogLevel, **kwargs) -> None:
        # kwargs defaults:
        printToConsole = True if "printToConsole" not in kwargs else kwargs["printToConsole"]
        writeToFile = True if "writeToFile" not in kwargs else kwargs["writeToFile"]
        color = loglevel.color if "color" not in kwargs else kwargs["color"]

        if printToConsole and (int(loglevel) <= int(self.console_log_level)):
            if self.terminalSupportsColors and color:
                print(color + string + Colors.reset)
            else:
                print(string)

        # Config is not loaded, write to buffer:
        if self.file_log_enabled is None:
            self.file_log_buffer.append({
                "string": string,
                "loglevel": loglevel
            })

        # Real file logging
        elif self.file_log_enabled and writeToFile:
            self.WriteFileLogLine(string, loglevel)

    def WriteFileLogLine(self, string: str, loglevel: LogLevel) -> None:
        if not self.file_log_descriptor \
                or not self.lock:
            raise Exception("File logging error! Descriptor or lock missing!")
        if int(loglevel) <= int(self.file_log_level):
            # acquire the lock
            with self.lock:
                self.file_log_descriptor.write(string+' \n')
            # so I can see the log in real time from a reader
            self.file_log_descriptor.flush()

    def CloseFile(self) -> None:
        if self.file_log_descriptor is not None:
            self.file_log_descriptor.close()
            self.file_log_descriptor = None


    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        preset.AddEntry(name="Console log level", key=CONFIG_KEY_CONSOLE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=consts.DEFAULT_LOG_LEVEL,
                        instruction="IOTURING_LOG_LEVEL envvar overwrites this setting!",
                        choices=LogLevelChoices)

        preset.AddEntry(name="Enable file logging", key=CONFIG_KEY_FILE_LOG_ENABLED,
                        question_type="yesno", default="N")

        preset.AddEntry(name="File log level", key=CONFIG_KEY_FILE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=consts.DEFAULT_LOG_LEVEL,
                        choices=LogLevelChoices)

        preset.AddEntry(name="File log path", key=CONFIG_KEY_FILE_LOG_PATH,
                        question_type="filepath", mandatory=True, default=cls.GetDefaultLogPath(),
                        instruction="Directory where log files will be saved")

        return preset

    @staticmethod
    def GetDefaultLogPath() -> str:

        default_path = Path(__file__).parent
        base_path = None

        if OsD.IsMacos() and macos_support:
            base_path = \
                Path(NSSearchPathForDirectoriesInDomains(  # type: ignore
                    NSLibraryDirectory,  # type: ignore
                    NSUserDomainMask, True)[0])  # type: ignore
        elif OsD.IsWindows():
            base_path = Path(OsD.GetEnv("LOCALAPPDATA"))
        elif OsD.IsLinux():
            if OsD.GetEnv("XDG_CACHE_HOME"):
                base_path = Path(OsD.GetEnv("XDG_CACHE_HOME"))
            elif OsD.GetEnv("HOME"):
                base_path = Path(OsD.GetEnv("HOME")).joinpath(".cache")

        if base_path:
            default_path = base_path.joinpath(App.getName())

        return str(default_path.joinpath(consts.LOGS_FOLDER))
