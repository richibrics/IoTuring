import platform # Platform detection

import json
import os  # Configurations file path manipulation, environment variables
import inspect # Configurations file path manipulation

from IoTuring.Logger.LogObject import LogObject
from IoTuring.MyApp.App import App # App name

# macOS dep (in PyObjC)
try:
    from AppKit import *
    from Foundation import *
    macos_support = True
except:
    macos_support = False

CONFIG_PATH_ENV_VAR = "IOTURING_CONFIG_DIR"

CONFIGURATION_FILE_NAME = "configurations.json"

# read ConfiguratorIO.checkConfigurationFileInOldLocation for more information
DONT_MOVE_FILE_FILENAME = "dontmoveconf.itg"

class ConfiguratorIO(LogObject):
    def __init__(self):
        self.directoryName = App.getName()
    
    def readConfigurations(self):
        """ Returns configurations dictionary. If does not exist the file where it should be stored, return None. """
        config = None
        try:
            with open(self.getFilePath(), "r") as f:
                config = json.loads(f.read())
            self.Log(self.LOG_MESSAGE, "Loaded \"" + self.getFilePath() + "\"")
        except:
            self.Log(self.LOG_WARNING, "It seems you don't have a configuration yet. Use configuration mode (-c) to enable your favourite entities and warehouses.\
                     \nConfigurations will be saved in \"" + self.getFolderPath() + "\"")
        return config
    
    def writeConfigurations(self, data):
        """ Writes configuration data in its file """
        self.createFolderPathIfDoesNotExist()
        with open(self.getFilePath(), "w") as f:
            f.write(json.dumps(data))
        self.Log(self.LOG_MESSAGE, "Saved \"" + self.getFilePath() + "\"")
        
    def checkConfigurationFileExists(self):
        """ Returns True if the configuration file exists in the correct folder, False otherwise. """
        return os.path.exists(self.getFilePath()) and os.path.isfile(self.getFilePath())
    
    def getFilePath(self):
        """ Returns the path to the configurations file. """
        return os.path.join(self.getFolderPath(), CONFIGURATION_FILE_NAME)
    
    def createFolderPathIfDoesNotExist(self):      
        """ Check if file exists, if not check if path exists: if not create both folder and file otherwise just the file """
        if not os.path.exists(self.getFolderPath()):    
            if not os.path.exists(self.getFolderPath()):
                os.makedirs(self.getFolderPath())        
    
    def getFolderPath(self):
        """ Returns the path to the configurations file. If the directory where the file
            will be stored doesn't exist, it will be created. """
            
        folderPath = self.defaultFolderPath()
        try:
            # Use path from environment variable if present, otherwise os specific folders, otherwise use default path
            envvarPath = self.envvarFolderPath()
            if envvarPath is not None:
                folderPath = envvarPath
            else:
                _os = platform.system()
                if _os == 'Darwin' and macos_support:
                    folderPath = self.macOSFolderPath()
                    folderPath = os.path.join(folderPath, self.directoryName)
                elif _os == "Windows":
                    folderPath = self.windowsFolderPath()        
                    folderPath = os.path.join(folderPath, self.directoryName)
                elif _os == "Linux":
                    folderPath = self.linuxFolderPath()
                    folderPath = os.path.join(folderPath, self.directoryName)
        except:
            pass # default folder path will be used
        
        # add slash if missing (for log reasons)
        if not folderPath.endswith(os.sep):
            folderPath += os.sep
            
        return folderPath

    def defaultFolderPath(self):
        return os.path.dirname(inspect.getfile(ConfiguratorIO))
    
    # https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html
    def macOSFolderPath(self):
        paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,True)
        basePath = (len(paths) > 0 and paths[0]) or NSTemporaryDirectory()
        return basePath
    
    # https://docs.microsoft.com/en-us/windows/win32/shell/knownfolderid
    def windowsFolderPath(self):
        return os.environ["APPDATA"]
    
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    def linuxFolderPath(self):
        return os.environ["XDG_CONFIG_HOME"] if "XDG_CONFIG_HOME" in os.environ else os.path.join(os.environ["HOME"], ".config")
    
    def envvarFolderPath(self):
        return os.getenv(CONFIG_PATH_ENV_VAR)
    
    # In versions prior to 2022.12.2, the configurations file was stored in the same folder as this file
    def oldFolderPath(self):
        return os.path.dirname(inspect.getfile(ConfiguratorIO))
    
    def checkConfigurationFileInOldLocation(self):
        """ Should be called at the beginning of the program when in -c mode.
            Checks if a config. file is in the old folder path; if so ask if user wants to copy it
            into new location, instead of rewriting it from zero.
            If yes, copy it; otherwise leave it there and write a don't move file to remmeber the 
            choose in the next times. 
            This check is not done if old path = current chosen path 
        """
        
        # This check is not done if old path = current chosen path (also check if ending slash is present)
        if self.oldFolderPath() == self.getFolderPath() or self.oldFolderPath() == self.getFolderPath()[:-1]:
            return
        
        # Exit check if no config. in old directory or if there is also the dont move file with it.
        configuration_file_exists = os.path.exists(os.path.join(self.oldFolderPath(), CONFIGURATION_FILE_NAME))
        dont_move_file_exists = os.path.exists(os.path.join(self.oldFolderPath(), DONT_MOVE_FILE_FILENAME))
        if not configuration_file_exists or (configuration_file_exists and dont_move_file_exists):
            return
        
        response = input("A configuration file was found in the old location. Do you want to move it to the new location ? if not, a new blank configuration will be used (y/n): ")
        response = bool( response.lower() == "y")
        # Then ask to move it
        if response:
            # create folder if not exists
            self.createFolderPathIfDoesNotExist()
            # copy file from old to new location
            os.rename(os.path.join(self.oldFolderPath(), CONFIGURATION_FILE_NAME), os.path.join(self.getFolderPath(), CONFIGURATION_FILE_NAME))
            self.Log(self.LOG_MESSAGE, "Copied into \"" + os.path.join(self.getFolderPath(), CONFIGURATION_FILE_NAME) + "\"")
        else:
            # create dont move file
            with open(os.path.join(self.oldFolderPath(), DONT_MOVE_FILE_FILENAME), "w") as f:
                f.write("This file is here to remember you that you don't want to move the configuration file into the new location. If you want to move it, delete this file and \
                    run the script in -c mode.")
            self.Log(self.LOG_MESSAGE, "You won't be asked again. A new blank configuration will be used; if you want to move the existing configuration file, delete \"" + os.path.join(self.oldFolderPath(), DONT_MOVE_FILE_FILENAME) + "\" and run the script in -c mode.")