from threading import Thread
import time

DEFAULT_LOOP_TIMEOUT = 3

class Warehouse():
    
    def __init__(self) -> None:
        self.entities = []
        self.loopTimeout = DEFAULT_LOOP_TIMEOUT

    def AddEntity(self, entityInstance) -> None:
        """ Add an entity instance to the warehouse's enitities """
        self.entities.append(entityInstance)

    def Start(self) -> None:
        """ Start a thread that will loop the Loop function"""
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

    def Loop(self) -> None:
        """ Must be implemented in subclasses """
        pass