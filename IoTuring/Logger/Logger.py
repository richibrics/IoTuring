from io import TextIOWrapper
import IoTuring.Logger.consts as consts
from IoTuring.Logger.Colors import Colors
import sys
import os  # to access directory functions
import inspect  # to get this file path
from datetime import datetime  # for logging purpose and filename
import json  # to print a dict easily
# Singleton pattern used


class Logger():

    from IoTuring.Logger.consts import LOG_INFO, LOG_MESSAGE, LOG_ERROR, LOG_DEBUG, LOG_DEVELOPMENT, LOG_WARNING
    __instance = None

    log_filename = ""
    log_file_descriptor = None

    def __init__(self) -> None:
        # Prepare the singleton
        if Logger.__instance != None:
            raise Exception(
                "This class is a singleton, use .getInstance() to access it!")
        else:
            Logger.__instance = self

        self.terminalSupportsColors = Logger.checkTerminalSupportsColors()
        
        # Prepare the log
        self.SetLogFilename()

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

    def Log(self, messageType, source, message) -> None:
        if type(message) == dict:
            self.LogDict(messageType, source, message)
            return  # Log dict will call this function so I don't need to go down at the moment
        elif type(message) == list:
            self.LogList(messageType, source, message)
            return  # Log list will call this function so I don't need to go down at the moment

        message = str(message)
        # Call this function for each line of the message if there are more than one line.
        messageLines = message.split("\n")
        if len(messageLines) > 1:
            for line in messageLines:
                self.Log(messageType, source, line)
            return  # Stop the function then because I've already called this function from each line so I don't have to go down here

        if messageType == self.LOG_INFO:
            messageTypeString = 'Info'
        elif messageType == self.LOG_ERROR:
            messageTypeString = 'Error'
        elif messageType == self.LOG_WARNING:
            messageTypeString = 'Warning'
        elif messageType == self.LOG_DEBUG:
            messageTypeString = 'Debug'
        elif messageType == self.LOG_MESSAGE:
            messageTypeString = 'Message'
        elif messageType == self.LOG_DEVELOPMENT:
            messageTypeString = 'Dev'
        else:
            messageTypeString = 'Logger'

        prestring = '[ '+self.GetMessageDatetimeString()+' | '+messageTypeString.center(consts.STRINGS_LENGTH[0]) + ' | ' + source.center(consts.STRINGS_LENGTH[1])+']' + \
            consts.PRESTRING_MESSAGE_SEPARATOR_LEN*' '  # justify

        # Manage string to print in more lines if it's too long
        while len(message) > 0:
            string = prestring+message[:consts.MESSAGE_WIDTH]
            # Cut for next iteration if message is longer than a line
            message = message[consts.MESSAGE_WIDTH:]
            # then I add the dash to the row
            if(len(message) > 0 and string[-1] != " " and string[-1] != "." and string[-1] != ","):
                string = string + '-'  # Print new line indicator if I will go down in the next iteration
            self.PrintAndSave(string, messageType)
            # -1 + space cause if the char in the prestring isn't a space, it will be directly attached to my message without a space

            prestring = (len(prestring)-consts.PRESTRING_MESSAGE_SEPARATOR_LEN) * \
                consts.LONG_MESSAGE_PRESTRING_CHAR+consts.PRESTRING_MESSAGE_SEPARATOR_LEN*' '

        # After log I close the file so the log is visible outside the script # TODO Better way to do this without closing always the file ?
        self.CloseFile()

    def LogDict(self, messageLevel, source, dict):
        try:
            string = json.dumps(dict, indent=4, sort_keys=False,
                                default=lambda o: '<not serializable>')
            lines = string.splitlines()
            for line in lines:
                self.Log(messageLevel, source, "> "+line)
        except Exception as e:
            self.Log(self.LOG_ERROR, source, "Can't print dictionary content")

    def LogList(self, messageLevel, source, _list):
        try:
            for index, item in enumerate(_list):
                if type(item) == dict or type(item) == list:
                    self.Log(messageLevel, source, "Item #"+str(index))
                    self.Log(messageLevel, source, item)
                else:
                    self.Log(messageLevel, source, str(
                        index) + ": " + str(item))

        except:
            self.Log(self.LOG_ERROR, source, "Can't print dictionary content")

    # Both print and save to file

    def PrintAndSave(self, string, level) -> None:
        if level <= consts.CONSOLE_LOG_LEVEL:
            self.ColoredPrint(string, level)
        if level <= consts.FILE_LOG_LEVEL:
            self.GetLogFileDescriptor().write(string+' \n')

    def ColoredPrint(self, string, level) -> None:
        if not self.terminalSupportsColors:
            print(string)
        elif level == self.LOG_INFO:
            print(string)
        elif level == self.LOG_WARNING:
            print(Colors.yellow + string + Colors.reset)
        elif level == self.LOG_ERROR:
            print(Colors.red + string + Colors.reset)
        elif level == self.LOG_MESSAGE:
            print(Colors.green + string + Colors.reset)
        else:
            print(string)

    def GetLogFileDescriptor(self) -> TextIOWrapper:
        if self.log_file_descriptor is None:
            self.log_file_descriptor = open(self.log_filename, "a")

        return self.log_file_descriptor

    def CloseFile(self) -> None:
        if self.log_file_descriptor is not None:
            self.log_file_descriptor.close()
            self.log_file_descriptor = None

    # Singleton method
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Logger.__instance == None:
            Logger()
        return Logger.__instance

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