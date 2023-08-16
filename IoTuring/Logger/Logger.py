from io import TextIOWrapper
from IoTuring.Logger import consts
from IoTuring.Logger.LogLevel import LogLevelObject, LogLevel
import sys
import os
import inspect
from datetime import datetime
import json
import threading


class Singleton(type):
    """ Metaclass for singleton classes """

    # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python/6798042#6798042

    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__()
        return cls._instances[cls]


class Logger(LogLevelObject, metaclass=Singleton):

    lock = threading.Lock()

    log_filename = ""
    log_file_descriptor = None

    def __init__(self) -> None:

        self.terminalSupportsColors = Logger.checkTerminalSupportsColors()

        # Prepare the log
        self.SetLogFilename()
        # Open the file descriptor
        self.GetLogFileDescriptor()

    def SetLogFilename(self) -> str:
        """ Set filename with timestamp and also call setup folder """
        dateTimeObj = datetime.now()
        self.log_filename = os.path.join(
            self.SetupFolder(), dateTimeObj.strftime(consts.LOG_FILENAME_FORMAT).replace(":", "_"))
        return self.log_filename

    def SetupFolder(self) -> str:
        """ Check if exists (or create) the folder of logs inside this file's folder """
        thisFolder = os.path.dirname(inspect.getfile(Logger))
        newFolder = os.path.join(thisFolder, consts.LOGS_FOLDER)
        if not os.path.exists(newFolder):
            os.mkdir(newFolder)

        return newFolder

    def GetMessageDatetimeString(self) -> str:
        now = datetime.now()
        return now.strftime(consts.MESSAGE_DATETIME_FORMAT)

    # LOG

    def Log(self, loglevel: LogLevel, source: str, message, printToConsole=True, writeToFile=True) -> None:
        if type(message) == dict:
            self.LogDict(loglevel, source, message,
                         printToConsole, writeToFile)
            return  # Log dict will call this function so I don't need to go down at the moment
        elif type(message) == list:
            self.LogList(loglevel, source, message,
                         printToConsole, writeToFile)
            return  # Log list will call this function so I don't need to go down at the moment

        message = str(message)
        # Call this function for each line of the message if there are more than one line.
        messageLines = message.split("\n")
        if len(messageLines) > 1:
            for line in messageLines:
                self.Log(loglevel, source, line,
                         printToConsole, writeToFile)
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
            self.PrintAndSave(string, loglevel, printToConsole, writeToFile)
            # -1 + space cause if the char in the prestring isn't a space, it will be directly attached to my message without a space

            prestring = (len(prestring)-consts.PRESTRING_MESSAGE_SEPARATOR_LEN) * \
                consts.LONG_MESSAGE_PRESTRING_CHAR+consts.PRESTRING_MESSAGE_SEPARATOR_LEN*' '

    def LogDict(self, loglevel, source, message_dict: dict, *args):
        try:
            string = json.dumps(message_dict, indent=4, sort_keys=False,
                                default=lambda o: '<not serializable>')
            lines = string.splitlines()
            for line in lines:
                self.Log(loglevel, source, "> "+line, *args)
        except Exception as e:
            self.Log(self.LOG_ERROR, source, "Can't print dictionary content")

    def LogList(self, loglevel, source, message_list: list, *args):
        try:
            for index, item in enumerate(message_list):
                if type(item) == dict or type(item) == list:
                    self.Log(loglevel, source, "Item #"+str(index), *args)
                    self.Log(loglevel, source, item, *args)
                else:
                    self.Log(loglevel, source,
                             f"{str(index)}: {str(item)}", *args)

        except:
            self.Log(self.LOG_ERROR, source, "Can't print dictionary content")

    # Both print and save to file
    def PrintAndSave(self, string, loglevel: LogLevel, printToConsole=True, writeToFile=True) -> None:
        # Override log level from envvar:
        console_level = consts.CONSOLE_LOG_LEVEL
        if os.getenv("IOTURING_LOG_LEVEL"):
            console_level = str(os.getenv("IOTURING_LOG_LEVEL"))

        console_log_level = LogLevel(console_level)
        file_log_level = LogLevel(consts.FILE_LOG_LEVEL)

        if printToConsole and int(loglevel) <= int(console_log_level):
            self.ColoredPrint(string, loglevel)

        if writeToFile and int(loglevel) <= int(file_log_level):
            # acquire the lock
            with self.lock:
                self.GetLogFileDescriptor().write(string+' \n')
            # so I can see the log in real time from a reader
            self.GetLogFileDescriptor().flush()

    def ColoredPrint(self, string, loglevel: LogLevel) -> None:
        if not self.terminalSupportsColors:
            print(string)
        else:
            print(loglevel.get_colored_string(string))

    def GetLogFileDescriptor(self) -> TextIOWrapper:
        if self.log_file_descriptor is None:
            self.log_file_descriptor = open(self.log_filename, "a")

        return self.log_file_descriptor

    def CloseFile(self) -> None:
        if self.log_file_descriptor is not None:
            self.log_file_descriptor.close()
            self.log_file_descriptor = None

    @staticmethod
    def checkTerminalSupportsColors():
        """
        Returns True if the running system's terminal supports color, and False
        otherwise.
        """
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                      'ANSICON' in os.environ)
        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        return supported_platform and is_a_tty
