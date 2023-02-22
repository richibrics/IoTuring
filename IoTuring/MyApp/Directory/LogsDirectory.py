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
    
    # get the folder on windows where to store application log file
    def _windowsFolderPath(self):
        # return joined local app data folder and "Logs" subfolder
        return os.path.join(os.environ["LOCALAPPDATA"], "Logs")
    
    # get the folder where linux stores all the application log files
    def _linuxFolderPath(self):
        # There is no standard in the XDG spec for logs, so place it in $XDG_CACHE_HOME, and fallback to $HOME/.cache
        if "XDG_CACHE_HOME" in os.environ:
            return os.path.join(os.environ["XDG_CACHE_HOME"], "Logs")
        else:
            return os.path.join(os.environ["HOME"], ".cache", "Logs")
            