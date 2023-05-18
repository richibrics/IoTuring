from threading import Thread
from IoTuring.Logger.LogObject import LogObject
# Singleton pattern used


class EntityManager(LogObject):

    __instance = None

    def __init__(self) -> None:
        # Prepare the singleton
        if EntityManager.__instance != None:
            raise Exception(
                "This class is a singleton, use .getInstance() to access it!")
        else:
            EntityManager.__instance = self

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

    def GetEntities(self) -> list:
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

    # Singleton method

    @staticmethod
    def getInstance():
        """ Static access method. """
        if EntityManager.__instance == None:
            EntityManager()
        return EntityManager.__instance
