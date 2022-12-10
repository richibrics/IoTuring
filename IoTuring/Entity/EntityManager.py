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

        # Where I store the entities that are only used as dependencies so with a passive behaviour: only pass value to other Entity(s)
        self.passiveEntities = []

    @staticmethod
    def EntityNameToClass(name):  # TODO Implement
        """ Get entity name and return its class """
        raise NotImplementedError()

    def AddActiveEntity(self, entity):
        """ Pass an entity instance, add to list of active entities """
        self.activeEntities.append(entity)

    def AddPassiveEntity(self, entity):
        """ Pass an entity instance, add to list of passive entities """
        self.passiveEntities.append(entity)

    def Start(self):
        self.InitializeEntities()
        self.PostInitializeEntities()
        self.ManageUpdates()

    def GetEntities(self, includePassive) -> list:
        """ 
            Return a list with entities.
            includePassive = True: returns all entities (included those that were loaded due to dependencies)
            includePassive = False: returns only entities that can send and receive data to/from warehouses. 
        """
        if not includePassive:
            return self.activeEntities
        else:
            return self.activeEntities + self.passiveEntities

    def UnloadEntity(self, entity):
        """ Unloads the passed entity """
        if entity in self.activeEntities:
            self.activeEntities.remove(entity)
        elif entity in self.passiveEntities:
            self.passiveEntities.remove(entity)
        else:
            raise Exception("Can't unload the requested entity: not found among loaded entities.")
        self.Log(self.LOG_INFO, entity.GetEntityId() + " unloaded")

    def InitializeEntities(self):
        for entity in self.GetEntities(includePassive=True):
            if not entity.CallInitialize():
                self.UnloadEntity(entity) # if errors, unload

    def PostInitializeEntities(self):
        for entity in self.GetEntities(includePassive=True):
            if not entity.CallPostInitialize():
                self.UnloadEntity(entity) # if errors, unload

    def ManageUpdates(self):
        """ Start a thread for each entity in which it will update periodically """
        for entity in self.GetEntities(includePassive=True):
            thread = Thread(target=entity.LoopThread)
            thread.daemon = True
            thread.start()

    def GetDependentEntitySensorValue(self, callerEntity, entityToFind: str, dataKeyToFind: str):
        """ Called by "callerEntity", return the value of "entityToFind"."dataKeyToFind" if it has value and if the callerEntity has the permission to access that entity.
            Permission is granted if "entityToFind" is present in "callerEntity".GetDependenciesList() """
        if entityToFind in callerEntity.GetDependenciesList():  # The entity to find must be in the list of entities that the caller entity (the one that wants the other entity) asked in the dependencies
            for entity in self.GetEntities(includePassive=True):
                if entity.GetEntityName() == entityToFind:
                    if not entity.GetEntitySensorByKey(dataKeyToFind).HasValue():
                        raise Exception(
                            "The Entity sensor you asked for hasn't got a value")
                    # I don't return the entity or the entitydata, because I don't want any edit from outside its entity !
                    return entity.GetEntitySensorByKey(dataKeyToFind).GetValue()

    def CheckEntityDependenciesSatisfied(self, callerEntity) -> list:
        """ Returns all the Entities specified in an entity dependencies list that have not been initialized,
            which means they could have been not activated from the configuration or not working correctly """
        not_found_deps = callerEntity.GetDependenciesList()
        for dependency in callerEntity.GetDependenciesList():
            for entity in self.GetEntities(True):
                if dependency == entity.__class__.__name__:
                    not_found_deps.remove(dependency)
        return not_found_deps

    # Singleton method

    @staticmethod
    def getInstance():
        """ Static access method. """
        if EntityManager.__instance == None:
            EntityManager()
        return EntityManager.__instance
