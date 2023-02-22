import platform
import os
import sys
from importlib_metadata import metadata


class GetDirectory():
    """ Class to get the path to the folder where things are stored in the system.
        It will try to get the path from the environment variable IOTURING_PATH, if it is not set
        it will use the default path for the OS.
        
        There are 3 os-specific methods to get the default path.
        
        Path selection is done in the following order:
            1. Environment variable
            2. OS-specific method
            3. Default path
        
        Once the path is obtained, it will be joined with the directory name of the application.
        
        e.g.:
            - by ENVVAR: CHOSEN_PATH 
            - Windows: C:\\Users\\username\\AppData\\Roaming\\ + IoTuring
            - macOS: /Users/username/Library/Application Support/ + IoTuring/
            - Linux: /home/username/.config/ + IoTuring/
            - if error: default path
            
        In addition, if default path is used and SUBFOLDER_NAME is set, it will be joined with the path.
        
        e.g.:
            - by ENVVAR: CHOSEN_PATH - like above
            - Windows: C:\\Users\\username\\AppData\\Roaming\\ + IoTuring - like above
            - if error: default path + SUBFOLDER_NAME 
    """
            
    PATH_ENVVAR_NAME = "IOTURING_PATH"  # Environment variable name, default one
    SUBFOLDER_NAME = None 
        
    APP_NAME = metadata('IoTuring')['Name']
    
    def getFolderPath(self):
        """ Returns the path to the folder where the application will store its data. """
        folderPath = self._defaultFolderPath()
        try:
            # Use path from environment variable if present, otherwise os specific folders, otherwise use default path
            envvarPath = self._envvarFolderPath()
            if envvarPath is not None:
                folderPath = envvarPath
            else:
                _os = platform.system()
                if _os == 'Darwin':
                    folderPath = self._macOSFolderPath()
                    folderPath = os.path.join(folderPath, self.APP_NAME)
                elif _os == "Windows":
                    folderPath = self._windowsFolderPath()        
                    folderPath = os.path.join(folderPath, self.APP_NAME)
                elif _os == "Linux":
                    folderPath = self._linuxFolderPath()
                    folderPath = os.path.join(folderPath, self.APP_NAME)
        except:
            folderPath = self._defaultFolderPath() # default folder path will be used
                
        # add slash if missing (for log reasons)
        if not folderPath.endswith(os.sep):
            folderPath += os.sep
        
        return folderPath
        
        
    def _macOSFolderPath(self):
        """ Returns the path to the folder where the application will store its data in macOS """
        raise NotImplementedError("_macOSFolderPath() is not implemented yet")
        
    def _windowsFolderPath(self):
        """ Returns the path to the folder where the application will store its data in Windows """
        raise NotImplementedError("_windowsFolderPath() is not implemented yet")
        
    def _linuxFolderPath(self):
        """ Returns the path to the folder where the application will store its data in Linux """
        raise NotImplementedError("_linuxFolderPath() is not implemented yet")

    def _envvarFolderPath(self):
        """ Returns the path to the folder where the application will store its data from the environment variable; None if not set.
            The environment variable name must be stored in self.PATH_ENVVAR_NAME """
        # Get path from environment variable
        return os.environ.get(self.PATH_ENVVAR_NAME)
    
    def _defaultFolderPath(self):
        """ Returns the path to the folder where the application will store its data in the default path.
            If not overriden, it will return IoTuring install directory + "UserFiles/" + [SUBFOLDER_NAME if not None]"""
        if self.SUBFOLDER_NAME is None:
            return os.path.join(os.path.dirname(os.path.realpath(sys.modules['__main__'].__file__)), "UserFiles")
        else:
            return os.path.join(os.path.dirname(os.path.realpath(sys.modules['__main__'].__file__)), "UserFiles", self.SUBFOLDER_NAME)