from os import fchdir

class App():
    NAME = "DomoticTuring"
    DESCRIPTION_FILENAME = "App/description.txt"

    # Version
    MAJOR_VERSION = "0"
    MINOR_VERSION = "0"
    REVISION_NUMBER = "1"

    @staticmethod 
    def getName() -> str:
        return App.NAME

    @staticmethod 
    def getDescription() -> str:
        try:
            with open(App.DESCRIPTION_FILENAME,"r") as f:
                return f.read()
        except:
            print("Can't get App description")
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
