import os
from pathlib import Path
from os import path
import importlib.util
import importlib.machinery
import sys
import inspect
from IoTuring.Logger.LogObject import LogObject

# from IoTuring.ClassManager import consts

# This is a parent class

# Implement subclasses in this way:

# def __init__(self):
#     ClassManager.__init__(self)
#     self.baseClass = Entity  : Select the class to find
#     self.GetModulesFilename(consts.ENTITIES_PATH)  : Select path where it should look for classes and add all classes to found list

# This class is used to find and load classes without importing them
# The important this is that the class is inside a folder that exactly the same name of the Class and of the file (obviously not talking about extensions)


class ClassManager(LogObject):
    def __init__(self):
        self.modulesFilename = []
        module_path = sys.modules[self.__class__.__module__].__file__
        if not module_path:
            raise Exception("Error getting path: " + str(module_path))
        else:
            self.mainPath = path.dirname(path.abspath(module_path))
        # THIS MUST BE IMPLEMENTED IN SUBCLASSES, IS THE CLASS I WANT TO SEARCH !!!!
        self.baseClass = None

    def GetClassFromName(self, wantedName):
        # From name, load the correct module and extract the class
        for module in self.modulesFilename:  # Search the module file
            moduleName = self.ModuleNameFromPath(module)
            # Check if the module name matches the given name
            if wantedName == moduleName:
                # Load the module
                loadedModule = self.LoadModule(module)
                # Now get the class
                return self.GetClassFromModule(loadedModule)
        return None

    def LoadModule(self, path):  # Get module and load it from the path
        try:
            loader = importlib.machinery.SourceFileLoader(
                self.ModuleNameFromPath(path), path)
            spec = importlib.util.spec_from_loader(loader.name, loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            moduleName = os.path.split(path)[1][:-3]
            sys.modules[moduleName] = module
        except Exception as e:
            self.Log(self.LOG_ERROR, "Error while loading module " +
                     path + ": " + str(e))
        return module

    # From the module passed, I search for a Class that has classNmae=moduleName
    def GetClassFromModule(self, module):
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if(name == module.__name__):
                    return obj

    # List files in the _path directory and get only files in subfolders
    def GetModulesFilename(self, _path):
        classesRootPath = path.join(self.mainPath, _path)
        if os.path.exists(classesRootPath):
            self.Log(self.LOG_DEVELOPMENT,
                     "Looking for python files in \"" + _path + os.sep + "\"...")
            result = list(Path(classesRootPath).rglob("*.py"))
            entities = []
            for file in result:
                filename = str(file)
                # TO check if a py files is in a folder !!!! with the same name !!! (same without extension)
                pathList = filename.split(os.sep)
                if len(pathList) >= 2:
                    if pathList[len(pathList)-1][:-3] == pathList[len(pathList)-2]:
                        entities.append(filename)

            self.modulesFilename = self.modulesFilename + entities
            self.Log(self.LOG_DEVELOPMENT, "Found " +
                     str(len(entities)) + " modules files")

    def ModuleNameFromPath(self, path):
        classname = os.path.split(path)
        return classname[1][:-3]

    def ListAvailableClassesNames(self) -> list:
        res = []
        for py in self.modulesFilename:
            res.append(path.basename(py).split(".py")[0])
        return res
