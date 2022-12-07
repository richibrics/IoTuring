from IoTuring.Configurator.MenuPreset import BooleanAnswers
from IoTuring.Logger.LogObject import LogObject
from IoTuring.Entity.EntityManager import EntityManager

from threading import Thread
import time

DEFAULT_LOOP_TIMEOUT = 10


class Warehouse(LogObject):
    NAME = "Unnamed"

    def __init__(self, configurations) -> None:
        self.loopTimeout = DEFAULT_LOOP_TIMEOUT
        self.configurations = configurations

    def Start(self) -> None:
        """ Initial configuration and start the thread that will loop the Warehouse.Loop() function"""
        thread = Thread(target=self.LoopThread)
        thread.daemon = True
        thread.start()

    def SetLoopTimeout(self, timeout) -> None:
        """ Set a timeout between 2 loops """
        self.loopTimeout = timeout

    def ShouldCallLoop(self) -> bool:
        """ Wait the timeout time and then tell it can run the Loop function """
        time.sleep(self.loopTimeout)
        return True

    def LoopThread(self) -> None:
        """ Entry point of the warehouse thread, will run Loop() periodically """
        self.Loop()  # First call without sleep before
        while(True):
            if self.ShouldCallLoop():
                self.Loop()

    def GetEntities(self) -> list:
        return EntityManager.getInstance().GetEntities(includePassive=False)

    # Called by "LoopThread", with time constant defined in "ShouldCallLoop"
    def Loop(self) -> None:
        """ Must be implemented in subclasses, autorun at Warehouse __init__ """
        raise NotImplementedError(
            "Please implement Loop method for this Warehouse")

    def GetWarehouseName(self) -> str:
        return self.NAME

    def GetWarehouseId(self) -> str:
        return "Warehouse." + self.GetWarehouseName()

    def LogSource(self):
        return self.GetWarehouseId()

    def GetConfigurations(self) -> dict:
        """ Safe return configurations dict """
        return self.configurations.copy()

    def GetFromConfigurations(self, key):
        """ Get value from confiugurations with key (if not present raise Exception) """
        if key in self.GetConfigurations():
            return self.GetConfigurations()[key]
        else:
            raise Exception("Can't find key " + key + " in configurations")

    def GetTrueOrFalseFromConfigurations(self, key):
        """ Get boolean value from confiugurations with key (if not present raise Exception) """
        value = self.GetFromConfigurations(key).lower()
        if value in BooleanAnswers.TRUE_ANSWERS:
            return True
        else:
            return False

    # Configuration methods
    @classmethod
    def ConfigurationPreset(self):
        """ Prepare a preset to manage settings insert/edit for the warehouse """
        return None
