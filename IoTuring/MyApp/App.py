import inspect
from Logger.Logger import Logger
import os

class App():
    NAME = "IoTuring"
    DESCRIPTION_FILENAME = "description.txt"
    VENDOR = "Riccardo Briccola"

    # Version
    MAJOR_VERSION = "1"
    MINOR_VERSION = "0"
    REVISION_NUMBER = "0"

    @staticmethod 
    def getName() -> str:
        return App.NAME
    
    @staticmethod 
    def getVendor() -> str:
        return App.VENDOR
    
    @staticmethod 
    def getDescription() -> str:
        thisFolder = os.path.dirname(inspect.getfile(App))
        path = os.path.join(thisFolder, App.DESCRIPTION_FILENAME)
        try:
            with open(path,"r") as f:
                return f.read()
        except:
            Logger.getInstance().Log(Logger.LOG_ERROR, "MyApp", "Can't get App description")
            return ""

    @staticmethod 
    def getVersion() -> str:
        return App.MAJOR_VERSION+"."+App.MINOR_VERSION+"."+App.REVISION_NUMBER
   
    def __str__(self) -> str:
        msg = ""
        msg += "Name: " + App.getName() + "\n"
        msg += "Version: " + App.getVersion() + "\n"
        msg += "Description: " + App.getDescription() + "\n"
        return msg
