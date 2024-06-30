import json
from pathlib import Path
import inspect
import sys

from IoTuring.Logger.LogObject import LogObject
from IoTuring.MyApp.App import App  # App name
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

# macOS dep (in PyObjC)
try:
    from AppKit import *  # type:ignore
    from Foundation import *  # type:ignore
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
            with open(self.getFilePath(), "r", encoding="utf-8") as f:
                config = json.loads(f.read())
            self.Log(self.LOG_INFO, f"Loaded \"{self.getFilePath()}\"")
        except FileNotFoundError:
            self.Log(self.LOG_WARNING, f"It seems you don't have a configuration yet. Use configuration mode (-c) to enable your favourite entities and warehouses.\
                     \nConfigurations will be saved in \"{str(self.getFolderPath())}\"")
        except Exception as e:
            self.Log(self.LOG_ERROR, f"Error opening configuration file: {str(e)}")
            sys.exit(str(e))
        return config

    def writeConfigurations(self, data):
        """ Writes configuration data in its file """
        try:
            self.createFolderPathIfDoesNotExist()
            with open(self.getFilePath(), "w", encoding="utf-8") as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False))
            self.Log(self.LOG_INFO, f"Saved \"{str(self.getFilePath())}\"")
        except Exception as e:
            self.Log(self.LOG_ERROR, f"Error saving configuration file: {str(e)}")
            sys.exit(str(e))

    def checkConfigurationFileExists(self) -> bool:
        """ Returns True if the configuration file exists in the correct folder, False otherwise. """
        try:
            return self.getFilePath().exists() and self.getFilePath().is_file()
        except:
            return False

    def getFilePath(self) -> Path:
        """ Returns the path to the configurations file. """
        return self.getFolderPath().joinpath(CONFIGURATION_FILE_NAME)

    def createFolderPathIfDoesNotExist(self):
        """ Check if file exists, if not check if path exists: if not create both folder and file otherwise just the file """
        if not self.getFolderPath().exists():
            self.getFolderPath().mkdir(parents=True)

    def getFolderPath(self) -> Path:
        """ Returns the path to the configurations file. If the directory where the file
            will be stored doesn't exist, it will be created. """

        folderPath = self.defaultFolderPath()
        try:
            # Use path from environment variable if present, otherwise os specific folders, otherwise use default path
            envvarPath = OsD.GetEnv(CONFIG_PATH_ENV_VAR)
            if envvarPath and len(envvarPath) > 0:
                folderPath = Path(envvarPath)
            else:
                if OsD.IsMacos() and macos_support:
                    folderPath = self.macOSFolderPath().joinpath(self.directoryName)
                elif OsD.IsWindows():
                    folderPath = self.windowsFolderPath().joinpath(self.directoryName)
                elif OsD.IsLinux():
                    folderPath = self.linuxFolderPath().joinpath(self.directoryName)

        except:
            pass  # default folder path will be used

        return folderPath

    def defaultFolderPath(self) -> Path:
        return Path(inspect.getfile(ConfiguratorIO)).parent

    # https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html
    def macOSFolderPath(self) -> Path:
        paths = NSSearchPathForDirectoriesInDomains(  # type: ignore
            NSApplicationSupportDirectory, NSUserDomainMask, True)  # type: ignore
        basePath = (len(paths) > 0 and paths[0]) \
            or NSTemporaryDirectory()  # type: ignore
        return Path(basePath)

    # https://docs.microsoft.com/en-us/windows/win32/shell/knownfolderid
    def windowsFolderPath(self) -> Path:
        return Path(OsD.GetEnv("APPDATA"))

    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    def linuxFolderPath(self) -> Path:
        if OsD.GetEnv("XDG_CONFIG_HOME"):
            path = Path(OsD.GetEnv("XDG_CONFIG_HOME"))
        else:
            path = Path(OsD.GetEnv("HOME")).joinpath(".config")
        return path

    # In versions prior to 2022.12.2, the configurations file was stored in the same folder as this file:
    def oldFolderPath(self) -> Path:
        return self.defaultFolderPath()

    def shouldMoveOldConfig(self) -> bool:
        """ Checks if a config file is in the old folder path and should be moved to the new location.

        Returns:
            bool: True if the config should be moved. False if old path = current chosen path or should not be moved
        """

        # This check is not done if old path = current chosen path:
        if self.oldFolderPath() == self.getFolderPath():
            return False

        # Old config does not exist:
        if not self.oldFolderPath().joinpath(CONFIGURATION_FILE_NAME).exists():
            return False
        # Old config and dont move file exists:
        elif self.oldFolderPath().joinpath(DONT_MOVE_FILE_FILENAME).exists():
            return False

        return True

    def manageOldConfig(self, moveFile: bool) -> None:
        """Move config file from old location, or create dontmove file

        Args:
            moveFile (bool): True: move the file. False: Create dontmove file
        """

        try:
            if moveFile:
                # create folder if not exists
                self.createFolderPathIfDoesNotExist()
                # copy file from old to new location
                self.oldFolderPath().joinpath(CONFIGURATION_FILE_NAME).rename(self.getFilePath())
                self.Log(self.LOG_INFO,
                        f"Copied to \"{str(self.getFilePath())}\"")
            else:
                # create dont move file
                with open(self.oldFolderPath().joinpath(DONT_MOVE_FILE_FILENAME), "w") as f:
                    f.write(" ".join([
                        "This file is here to remember you that you don't want to move the configuration file into the new location.",
                        "If you want to move it, delete this file and run the script in -c mode."
                    ]))
                self.Log(self.LOG_INFO, " ".join([
                    "You won't be asked again. A new blank configuration will be used;",
                    f"if you want to move the existing configuration file, delete \"{self.oldFolderPath().joinpath(DONT_MOVE_FILE_FILENAME)}",
                    "and run the script in -c mode."
                ]))
        except Exception as e:
            self.Log(self.LOG_ERROR, f"Error saving file: {str(e)}")
            sys.exit(str(e))
