import os
from .GetDirectory import GetDirectory

# macOS dep (in PyObjC)
try:
    from AppKit import *
    from Foundation import *
    macos_support = True
except:
    macos_support = False

class ConfigurationsDirectory(GetDirectory):
    PATH_ENVVAR_NAME = "IOTURING_CONFIG_DIR"  # Environment variable name
    SUBFOLDER_NAME = "Configurations"  # Subfolder name for configurations in default folder
    
    # https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html
    def _macOSFolderPath(self):
        paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,True)
        basePath = (len(paths) > 0 and paths[0]) or NSTemporaryDirectory()
        return basePath
    
    # https://docs.microsoft.com/en-us/windows/win32/shell/knownfolderid
    def _windowsFolderPath(self):
        return os.environ["APPDATA"]
    
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    def _linuxFolderPath(self):
        return os.environ["XDG_CONFIG_HOME"] if "XDG_CONFIG_HOME" in os.environ else os.path.join(os.environ["HOME"], ".config")
    