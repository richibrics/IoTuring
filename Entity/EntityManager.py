from typing import List
from xmlrpc.client import Boolean
from Entity.Entity import Entity
from Entity.Deployments.Username.Username import Username

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
    def EntityNameToClass(name) -> Entity: # TODO Implement
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

    def ManageUpdates(self): # TODO Implement
        """ Start a thread for each entity in which it will update periodically """
        for entity in self.GetEntities(includePassive=True):
            Thread(target=entity.LoopThread).start()
        
    # Singleton method
    @staticmethod
    def getInstance():
        """ Static access method. """
        if EntityManager.__instance == None:
            EntityManager()
        return EntityManager.__instance
