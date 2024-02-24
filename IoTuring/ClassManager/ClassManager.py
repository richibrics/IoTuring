from __future__ import annotations

from pathlib import Path
import importlib.util
import importlib.machinery
import sys
import inspect
from IoTuring.Logger.LogObject import LogObject

# This is a parent class

# This class is used to find and load classes without importing them
# The important this is that the class is inside a folder that exactly the same name of the Class and of the file (obviously not talking about extensions)


class ClassManager(LogObject):

    # Set up these class variables in subclasses:
    classesRelativePath = None  # Change in subclasses


    def __init__(self) -> None:

        classmanager_file_path = sys.modules[self.__class__.__module__].__file__
        if not classmanager_file_path:
            raise Exception("Error getting path: " +
                            str(classmanager_file_path))

        self.rootPath = Path(classmanager_file_path).parents[1]

        # Store loaded classes here:
        self.loadedClasses = []
        
        # Collect paths
        self.moduleFilePaths = self.GetModuleFilePaths()


    def GetModuleFilePaths(self) -> list:
        if not self.classesRelativePath:
            raise Exception("Path to deployments not defined")

        classesRootPath = self.rootPath.joinpath(self.classesRelativePath)

        if not classesRootPath.exists:
            raise Exception(f"Path does not exist: {classesRootPath}")

        self.Log(self.LOG_DEVELOPMENT,
                 f'Looking for python files in "{classesRootPath}"...')

        python_files = classesRootPath.rglob("*.py")

        # TO check if a py files is in a folder !!!! with the same name !!! (same without extension)
        filepaths = [f for f in python_files if f.stem == f.parent.stem]

        self.Log(self.LOG_DEVELOPMENT,
                 f"Found {str(len(filepaths))} modules files")

        return filepaths

    def GetClassFromName(self, wantedName: str) -> type | None:

        # Check from already loaded classes:
        module_class = next(
            (m for m in self.loadedClasses if m.__name__ == wantedName), None)

        if module_class:
            return module_class

        modulePath = next(
            (m for m in self.moduleFilePaths if m.stem == wantedName), None)

        if modulePath:

            loadedModule = self.LoadModule(modulePath)
            loadedClass = self.GetClassFromModule(loadedModule)
            self.loadedClasses.append(loadedClass)
            return loadedClass

        else:
            return None

    def LoadModule(self, module_path: Path):  # Get module and load it from the path
        try:
            loader = importlib.machinery.SourceFileLoader(
                module_path.stem, str(module_path))
            spec = importlib.util.spec_from_loader(loader.name, loader)

            if not spec:
                raise Exception("Spec not found")

            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            sys.modules[module_path.stem] = module
            return module
        except Exception as e:
            self.Log(self.LOG_ERROR,
                     f"Error while loading module {module_path.stem}: {str(e)}")

    # From the module passed, I search for a Class that has className=moduleName
    def GetClassFromModule(self, module):
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if (name == module.__name__):
                    return obj
        raise Exception(f"No class found: {module.__name__}")

    def ListAvailableClasses(self) -> list:

        return [self.GetClassFromName(f.stem) for f in self.moduleFilePaths]
