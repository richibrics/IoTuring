from threading import Thread

# Singleton pattern used
class EntityManager():

    __instance = None

    def __init__(self) -> None:
        # Prepare the singleton
        if EntityManager.__instance != None:
            raise Exception("This class is a singleton, use .getInstance() to access it!")
        else:
            EntityManager.__instance = self

        # Where I store the entities that update periodically that have an active behaviour: can send and receive data
        self.activeEntities = []

        # Where I store the entities that are only used as dependencies so with a passive behaviour: only pass value to other Entity(s)
        self.passiveEntities = []

    @staticmethod
    def EntityNameToClass(name): # TODO Implement
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
        """ Return a list with entities that update periodically that have an active behaviour: can send and receive data.
            Add also passive entities if asked (useful for dependency check/get) (False if it's a call by warehouse that wants to send the data!)"""
        if not includePassive:
            return self.activeEntities
        else:
            return self.activeEntities + self.passiveEntities

    def InitializeEntities(self):
        for entity in self.GetEntities(includePassive=True):
            entity.CallInitialize()

    def PostInitializeEntities(self):
        for entity in self.GetEntities(includePassive=True):
            entity.CallPostInitialize()

    def ManageUpdates(self): 
        """ Start a thread for each entity in which it will update periodically """
        for entity in self.GetEntities(includePassive=True):
            Thread(target=entity.LoopThread).start()
        

    def GetDependentEntitySensorValue(self, callerEntity, entityToFind: str, dataKeyToFind: str):
        """ Called by "callerEntity", return the value of "entityToFind"."dataKeyToFind" if it has value and if the callerEntity has the permission to access that entity.
            Permission is granted if "entityToFind" is present in "callerEntity".GetDependenciesList() """
        if entityToFind in callerEntity.GetDependenciesList(): # The entity to find must be in the list of entities that the caller entity (the one that wants the other entity) asked in the dependencies
            for entity in self.GetEntities(includePassive=True):
                if entity.GetEntityName() == entityToFind:
                    if not entity.GetEntitySensorByKey(dataKeyToFind).HasValue():
                        raise Exception("The Entity sensor you asked for hasn't got a value")
                    return entity.GetEntitySensorByKey(dataKeyToFind).GetValue() # I don't return the entity or the entitydata, because I don't want any edit from outside its entity !


    # Singleton method
    @staticmethod
    def getInstance():
        """ Static access method. """
        if EntityManager.__instance == None:
            EntityManager()
        return EntityManager.__instance
