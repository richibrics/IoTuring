from Logger.LogObject import LogObject
from Entity.EntityManager import EntityManager

from threading import Thread
import time

DEFAULT_LOOP_TIMEOUT = 30

class Warehouse(LogObject):
    name = "Unnamed"
    
    def __init__(self) -> None:
        self.loopTimeout = DEFAULT_LOOP_TIMEOUT

    def Start(self) -> None:
        """ Start a thread that will loop the Loop function"""
        self.RegisterEntityCommands()
        Thread(target=self.LoopThread).start()

    def SetLoopTimeout(self, timeout) -> None:
        """ Set a timeout between 2 loops """
        self.loopTimeout = timeout

    def ShouldCallLoop(self) -> bool:
        """ Wait the timeout time and then tell it can run the Loop function """
        time.sleep(self.loopTimeout)
        return True 

    def LoopThread(self) -> None:
        """ Entry point of the warehouse thread, will run Loop() periodically """
        while(True):
            if self.ShouldCallLoop():
                self.Loop()

    def GetEntities(self) -> list:
        return EntityManager.getInstance().GetEntities(includePassive=False)

    # Called by "LoopThread", with time constant defined in "ShouldCallLoop"
    def Loop(self) -> None:
        """ Must be implemented in subclasses, autoun at Warehouse __init__ """
        raise NotImplementedError("Please implement Loop method for this Warehouse")

    def GetWarehouseName(self) -> str:
        return self.name

    def GetWarehouseId(self) -> str:
        return "Warehouse." + self.GetWarehouseName()

    def LogSource(self):
        return self.GetWarehouseId()

    def RegisterEntityCommands(self):
        """ Method for sub-class, autoun at Warehouse __init__ to prepare the entity commands events"""    
        pass

    @classmethod
    def InstantiateWithConfiguration(self,configuration):
        """ Receive a configuration and instantiate the warehouse with the correct ordered parameters """
        return self() # here I only try to init without configurations (for those warehouses that do not override this function)

    @classmethod
    def ConfigurationPreset(self):
        """ Prepare a preset to manage settings insert/edit for the warehouse """
        return None