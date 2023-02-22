import os
from .GetDirectory import GetDirectory

# macOS dep (in PyObjC)
try:
    from AppKit import *
    from Foundation import *
    macos_support = True
except:
    macos_support = False

class LogsDirectory(GetDirectory):
    PATH_ENVVAR_NAME = "IOTURING_LOG_DIR"  # Environment variable name
    SUBFOLDER_NAME = "Logs"  # Subfolder name for configurations in default folder
    
    # get the folder where macos stores all the application log files
    def _macOSFolderPath(self):
        return os.path.join(NSSearchPathForDirectoriesInDomains(NSLibraryDirectory, NSUserDomainMask, True)[0], "Logs")
    
    # get the folder where windows stores all the application log files
    def _windowsFolderPath(self):
        return os.path.join(os.environ["APPDATA"], "Logs")
    
    # get the folder where linux stores all the application log files
    def _linuxFolderPath(self):
        return os.path.join(os.environ["HOME"], ".local", "share", "Logs")