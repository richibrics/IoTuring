from Entity.Entity import Entity
from Entity.Deployments.Username import Username

class EntityManager():

    def __init__(self) -> None:
        # Where I store the entities to update periodically
        self.entities = []

    @staticmethod
    def EntityNameToClass(name) -> Entity: # TODO: Implement
        """ Get entity name and return its class """
        return Username

    def NewEntity(self, entityClass) -> Entity: 
        """ Get an entity class, return an instantited entity (already added to my entites to update list) ready to be given to warehouses """
        entity = entityClass()
        self.entities.append(entity)
        return entity

    def Start(self):
        self.InitializeEntities()
        self.PostInitializeEntities()
        self.ManageUpdates()

    def InitializeEntities(self):
        for entity in self.entities:
            entity.CallInitialize()

    def PostInitializeEntities(self):
        for entity in self.entities:
            entity.CallPostInitialize()

    def ManageUpdates(self): # TODO: Implement
        """ Periodically update all the entities (async) """
        pass