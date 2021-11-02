from typing import List
from Exceptions.Exceptions import UnknownKeyException
from Logger.Logger import Logger
f

class Entity:
    __instance = None
    name = "Unnamed"

    def __init__(self) -> None:
        # Prepare the singleton
        if Entity.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Entity.__instance = self

        # Prepare the entity
        self.initializeState=False
        self.postinitializeState=False
        self.values = {}


    def Initialize(self):  # Implemented in sub-classes
        pass

    def CallInitialize(self): 
        try:
            self.Initialize()
            self.initializeState=True
            self.Log(Logger.LOG_INFO,"Initialization successfully completed")
        except Exception as e:
            self.Log(Logger.LOG_ERROR,"Initialization interrupted due to an error")
            self.Log(Logger.LOG_ERROR,e)
            del(self)
    

    def PostInitialize(self):  # Implemented in sub-classes
        pass

    def CallPostInitialize(self):  
        try:
            self.PostInitialize()
            self.postinitializeState=True
            self.Log(Logger.LOG_INFO,"Post-initialization successfully completed")
        except Exception as e:
            self.Log(Logger.LOG_ERROR,"Post-initialization interrupted due to an error")
            self.Log(Logger.LOG_ERROR,e)
            del(self)

    def AddKey(self,key) -> None:
        self.Log(Logger.LOG_DEBUG,"Add key " + key)
        self.values[key]=None

    def SetValue(self,key,value) -> None:
        if key in self.values:
            value = str(value)
            self.Log(Logger.LOG_DEBUG,"Set " + key + " to " + value)
            self.values[key]=value
        else:
            raise UnknownKeyException()

    def GetValue(self,key) -> str:
        if key in self.values:
            return self.values[key]
        else:
            raise UnknownKeyException()

    def KeyList(self) -> List:
        """ Return list of registered keys """
        return self.values.keys()

    def ShouldUpdate() -> bool:
        """ Return True if it's time to update """
        return True # TODO Implement this

    def Log(self, messageType, message):
        Logger.getInstance().Log(messageType, self.name + " Entity", message)
        
    # Singleton method
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Entity.__instance == None:
            Entity()
        return Entity.__instance
