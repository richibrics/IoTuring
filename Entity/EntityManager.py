from Entity.Entity import Entity
from Entity.Deployments.Username.Username import Username

from threading import Thread

class EntityManager():

    def __init__(self) -> None:
        # Where I store the entities to update periodically
        self.entities = []

    @staticmethod
    def EntityNameToClass(name) -> Entity: # TODO Implement
        """ Get entity name and return its class """
        return Username

    def NewEntity(self, entityClass) -> Entity: 
        """ Get an entity class, return an instantited entity (already added to my entites to update list) ready to be given to warehouses """
        entity = entityClass()
        if entity not in self.entities:
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

    def ManageUpdates(self): # TODO Implement
        """ Start a thread for each entity in which it will update periodically """
        for entity in self.entities:
            Thread(target=entity.LoopThread).start()
        