import consts
import os # to access directory functions
import inspect # to get this file path
from datetime import datetime # for logging purpose and filename

class Logger():
    __instance = None

    log_filename = ""

    def __init__(self) -> None:
        # Prepare the singleton
        if Logger.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self
        
        # Prepare the log
        self.GetLogFilename()
        # TODO continue !

    def GetLogFilename(self) -> str:
        dateTimeObj = datetime.now()
        return dateTimeObj.strftime(consts.LOG_FILENAME_FORMAT)
    
    def SetupFolder(self) -> str:
        """ Check if exists (or create) the folder of logs inside this file's folder """
        thisFolder = os.path.dirname(inspect.getfile(Logger.__class__))
        newFolder = os.path.join(thisFolder, consts.LOGS_FOLDER)
        if not os.path.exists(newFolder):
            os.mkdir(newFolder)

        return newFolder     


    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Logger.__instance == None:
            Logger()
        return Logger.__instance