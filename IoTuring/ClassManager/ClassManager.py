from __future__ import annotations

import importlib.util
import importlib.machinery
import sys
import inspect
from pathlib import Path

from IoTuring.ClassManager.consts import *
from IoTuring.Logger.LogObject import LogObject
from IoTuring.MyApp.App import App


class ClassManager(LogObject):
    """Base class for ClassManagers

    This class is used to find and load classes without importing them
    The important this is that the class is inside a folder that exactly the same name of the Class and of the file (obviously not talking about extensions)
    """

    def __init__(self, class_key:str) -> None:

        if class_key not in CLASS_PATH:
            raise Exception(f"Invalid class key {class_key}")
        else:
            self.classesRelativePath = CLASS_PATH[class_key]

        # Store loaded classes here:
        self.loadedClasses = []

        # Collect paths
        self.moduleFilePaths = self.GetModuleFilePaths()

    def GetModuleFilePaths(self) -> list[Path]:
        """Get the paths of of python files of this class

        Raises:
            Exception: If path not defined or exists
            FileNotFoundError: No module in the dir

        Returns:
            list[Path]: List of paths of python files
        """

        if not self.classesRelativePath:
            raise Exception("Path to deployments not defined")

        # Get the absolute path of the dir of files:
        classesRootPath = App.getRootPath().joinpath(self.classesRelativePath)

        if not classesRootPath.exists:
            raise Exception(f"Path does not exist: {classesRootPath}")

        self.Log(self.LOG_DEBUG,
                 f'Looking for python files in "{classesRootPath}"...')

        python_files = classesRootPath.rglob("*.py")

        # Check if a py files are in a folder with the same name !!! (same without extension)
        filepaths = [f for f in python_files if f.stem == f.parent.stem]

        if not filepaths:
            raise FileNotFoundError(
                f"No module files found in {classesRootPath}")

        self.Log(self.LOG_DEBUG,
                 f"Found {str(len(filepaths))} modules files")

        return filepaths

    def GetClassFromName(self, wantedName: str) -> type | None:
        """Get the class of given name, and load it

        Args:
            wantedName (str): The name to look for

        Returns:
            type | None: The class if found, None if not found
        """

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
        """Get all classes of this ClassManager

        Returns:
            list: The list of classes
        """

        return [self.GetClassFromName(f.stem) for f in self.moduleFilePaths]
