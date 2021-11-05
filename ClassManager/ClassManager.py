import os
from Entity.Entity import Entity
from pathlib import Path
from os import path
import importlib.util
import importlib.machinery
import sys, inspect
from Logger.Logger import Logger
from ClassManager import consts

class ClassManager(): # Class to load Entities from the Entitties dir and get them from name 
    def __init__(self):
        self.logger=Logger()
        self.modulesFilename=[]
        self.mainPath = path.dirname(path.abspath(
            sys.modules[self.__class__.__module__].__file__))
        self.GetModulesFilename(consts.ENTITIES_PATH) 
        # self.GetModulesFilename(consts.CUSTOM_ENTITIES_PATH) # TODO Decide if I'll use customs

    def GetEntityClass(self,entityName):
        # From entity name, load the correct module and extract the entity class
        for module in self.modulesFilename: # Search the module file
            moduleName=self.ModuleNameFromPath(module)
            # Check if the module name matches the entity sname
            if entityName==moduleName:
                # Load the module
                loadedModule=self.LoadModule(module)
                return self.GetEntityClassFromModule(loadedModule)
        return None


    def LoadModule(self,path): # Get module and load it from the path
        loader = importlib.machinery.SourceFileLoader(self.ModuleNameFromPath(path), path)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        moduleName=os.path.split(path)[1][:-3]
        sys.modules[moduleName]=module
        return module

    def GetEntityClassFromModule(self,module): # From the module passed, I search for a Class that has the Entity class as parent
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                for base in obj.__bases__: # Check parent class
                    if(base==Entity):
                        return obj


    def GetModulesFilename(self,_path): # List files in the Entities directory and get only files in subfolders
        entitiesPath=path.join(self.mainPath,_path)
        if os.path.exists(entitiesPath):
            self.Log(Logger.LOG_DEVELOPMENT,"Looking for Entity python file in \"" + _path + os.sep +  "\"...")
            result = list(Path(entitiesPath).rglob("*.py"))
            entities = []
            for file in result:
                filename = str(file)
                pathList= filename.split(os.sep) # TO check if a py files is in a folder with the same name (same without extension)
                if len(pathList)>=2:
                    if pathList[len(pathList)-1][:-3]==pathList[len(pathList)-2]: 
                        entities.append(filename)

            self.modulesFilename = self.modulesFilename + entities
            self.Log(Logger.LOG_DEVELOPMENT,"Found " + str(len(entities)) + " entity file")


    def ModuleNameFromPath(self,path):
        classname=os.path.split(path)
        return classname[1][:-3] 

    def ListAvailableEntities(self) -> str:
        res = []
        for py in self.modulesFilename:
            res.append(path.basename(py).split(".py")[0])
        return res

    def Log(self,_type,message):
        self.logger.Log(_type,"Class Manager",message)