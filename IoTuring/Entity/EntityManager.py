from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from IoTuring.Entity.Entity import Entity

from threading import Thread
from IoTuring.Logger.LogObject import LogObject
from IoTuring.Logger.Logger import Singleton


class EntityManager(LogObject, metaclass=Singleton):

    def __init__(self) -> None:

        # Where I store the entities that update periodically that have an active behaviour: can send and receive data
        self.activeEntities = []

    @staticmethod
    def EntityNameToClass(name):  # TODO Implement
        """ Get entity name and return its class """
        raise NotImplementedError()

    def AddActiveEntity(self, entity):
        """ Pass an entity instance, add to list of active entities """
        self.activeEntities.append(entity)

    def Start(self):
        self.InitializeEntities()
        self.ManageUpdates()

    def GetEntities(self) -> list[Entity]:
        """ 
            Return a list with entities.
        """
        return self.activeEntities

    def UnloadEntity(self, entity):
        """ Unloads the passed entity """
        if entity in self.activeEntities:
            self.activeEntities.remove(entity)
        else:
            raise Exception("Can't unload the requested entity: not found among loaded entities.")
        self.Log(self.LOG_INFO, entity.GetEntityId() + " unloaded")

    def InitializeEntities(self):
        for entity in self.GetEntities().copy():
            if not entity.CallInitialize():
                self.UnloadEntity(entity) # if errors, unload

    def ManageUpdates(self):
        """ Start a thread for each entity in which it will update periodically """
        for entity in self.GetEntities():
            
            # Only start threads for entities with Update() method:
            if not entity.Update.__qualname__ == "Entity.Update":
                thread = Thread(target=entity.LoopThread)
                thread.daemon = True
                thread.start()

