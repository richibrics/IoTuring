import platform # Platform detection

import os  # Configurations file path manipulation, environment variables
import inspect # Configurations file path manipulation

from IoTuring.MyApp.App import App # App name

# macOS dep (in PyObjC)
try:
    from AppKit import *
    from Foundation import *
    macos_support = True
except:
    macos_support = False


CONFIGURATION_FILE_NAME = "configurations.json"

class ConfiguratorIO:
    def __init__(self):
        self.directoryName = App.getName()
    
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
            _os = platform.system()
            if _os == 'Darwin' and macos_support:
                folderPath = self.macOSFolderPath()
            elif _os == "Windows":
                folderPath = self.windowsFolderPath()
            elif _os == "Linux":
                folderPath = self.linuxFolderPath()
        except:
            pass # default folder path will be used
        
        return os.path.join(folderPath, self.directoryName)

    def defaultFolderPath(self):
        return os.path.dirname(inspect.getfile(ConfiguratorIO))
    
    # https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html
    def macOSFolderPath(self):
        paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,True)
        basePath = (len(paths) > 0 and paths[0]) or NSTemporaryDirectory()
        return basePath
    
    # https://docs.microsoft.com/en-us/windows/win32/shell/knownfolderid
    def windowsFolderPath(self):
        return os.environ["PROGRAMDATA"] if platform.release() == "Server" else os.environ["APPDATA"]
    
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    def linuxFolderPath(self):
        return os.environ["XDG_CONFIG_HOME"] if "XDG_CONFIG_HOME" in os.environ else os.path.join(os.environ["HOME"], ".config")