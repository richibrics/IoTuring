from __future__ import annotations

from datetime import datetime
import json
import threading
from pathlib import Path



from IoTuring.Logger import consts
from IoTuring.Logger.LogLevel import LogLevelObject, LogLevel
from IoTuring.Logger.Colors import Colors
from IoTuring.Exceptions.Exceptions import UnknownLoglevelException

from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import TerminalDetection as TD



class Singleton(type):
    """ Metaclass for singleton classes """

    # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python/6798042#6798042

    _instances = {}

    def __call__(cls):  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__()
        return cls._instances[cls]


class Logger(LogLevelObject, metaclass=Singleton):

    startupTimeString = datetime.now().strftime(
        consts.LOG_FILENAME_FORMAT).replace(":", "_")

    terminalSupportsColors = TD.CheckTerminalSupportsColors()

    # Default log levels:
    console_log_level = LogLevel(consts.DEFAULT_LOG_LEVEL)
    file_log_level = LogLevel(consts.DEFAULT_LOG_LEVEL)

    # File logs stored here, before configurator loaded.
    file_log_buffer = []

    # For writing to file:
    file_log_descriptor = None
    lock = None

    def __init__(self) -> None:

        # Set loglevel from envvar:
        self.SetConsoleLogLevel()

        diag_strings = [
            "Logger Init",
            f"Console Loglevel: {str(self.console_log_level)}",
            f"File Loglevel: {str(self.file_log_level)}"
        ]


        self.Log(self.LOG_DEVELOPMENT, "Logger", diag_strings)



    def SetConsoleLogLevel(self, loglevel_string:str = ""):
        new_loglevel = None
        # Override log level from envvar:
        if OsD.GetEnv("IOTURING_LOG_LEVEL"):
            new_loglevel = self.SanitizeLoglevel(OsD.GetEnv("IOTURING_LOG_LEVEL"))

        # Read from config:
        if not new_loglevel and loglevel_string:
            new_loglevel = self.SanitizeLoglevel(loglevel_string)

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

    # Called from LogSettings
    def StartFileLogging(self, loglevel_string:str, log_dir_path:Path) -> None:
        
        self.file_log_level = self.SanitizeLoglevel(loglevel_string) or self.file_log_level


        if not log_dir_path.exists():
            log_dir_path.mkdir(parents=True)

        file_log_filename = log_dir_path.joinpath(self.startupTimeString)

        self.file_log_descriptor = \
            open(file_log_filename, "a", encoding="utf-8")

        self.lock = threading.Lock()

        self.Log(self.LOG_DEBUG, "Logger",
                     f"File Log setup finished.")

        # Write buffer to disk:
        while self.file_log_buffer:
            line = self.file_log_buffer[0]
            self.WriteFileLogLine(line["string"], line["loglevel"])
            del self.file_log_buffer[0]

    # Called from LogSettings
    def DisableFileLogging(self) -> None:
        self.file_log_buffer = None
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
        if self.file_log_buffer is not None:
            self.file_log_buffer.append({
                "string": string,
                "loglevel": loglevel
            })

        # Real file logging
        elif self.file_log_descriptor and writeToFile:
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


