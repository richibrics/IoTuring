from typing import List
from Exceptions.Exceptions import UnknownKeyException
from Logger.Logger import Logger
import time

DEFAULT_UPDATE_TIMEOUT = 10

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
        self.tag = ""
        self.initializeState=False
        self.postinitializeState=False
        self.values = {}
        self.valuesID = 0 # When I update the values this number changes (randomly) so each warehouse knows I have updated
        self.updateTimeout = DEFAULT_UPDATE_TIMEOUT


    def Initialize(self):
        """ Must be implemented in sub-classes """
        pass

    def CallInitialize(self): 
        """ Safe method to run the Initialize function """
        try:
            self.Initialize()
            self.initializeState=True
            self.Log(Logger.LOG_INFO,"Initialization successfully completed")
        except Exception as e:
            self.Log(Logger.LOG_ERROR,"Initialization interrupted due to an error")
            self.Log(Logger.LOG_ERROR,e)
            del(self)
    

    def PostInitialize(self): 
        """ Must be implemented in sub-classes """
        pass

    def CallPostInitialize(self):  
        """ Safe method to run the PostInitialize function """
        try:
            self.PostInitialize()
            self.postinitializeState=True
            self.Log(Logger.LOG_INFO,"Post-initialization successfully completed")
        except Exception as e:
            self.Log(Logger.LOG_ERROR,"Post-initialization interrupted due to an error")
            self.Log(Logger.LOG_ERROR,e)
            del(self)

    def CallUpdate(self):  # Call the Update method safely
        """ Safe method to run the Update function """
        try:
            self.Update()
        except Exception as exc:
            self.Log(Logger.LOG_ERROR, 'Error occured during update: ' + str(exc)) # TODO I need an exception manager
            # self.entityManager.UnloadEntity(self) # TODO Think how to improve this

    def Update(self):  #
        """ Must be implemented in sub-classes """
        # Can't be called directly, cause stops everything in exception, call only using CallUpdate
        pass  

    def AddKey(self,key) -> None:
        """ Register a key so after I can assign it a value """
        self.Log(Logger.LOG_DEBUG,"Add key " + key)
        self.values[key]=None

    def SetValue(self,key,value) -> None:
        """ Set the value for a key """
        if key in self.KeyList():
            value = str(value)
            self.Log(Logger.LOG_DEBUG,"Set " + key + " to " + value)
            self.values[key]=value
        else:
            raise UnknownKeyException()

    def GetValue(self,key) -> str:
        """ Get value using its key """
        if key in self.KeyList():
            return self.values[key]
        else:
            raise UnknownKeyException()

    def KeyList(self) -> List:
        """ Return list of registered keys """
        return list(self.values.keys())

    def GetGlobalKey(self, key) -> str:
        """ From a value key, return entityname.key to identify the value everywhere """
        return self.GetName() + "." + key

    def SetUpdateTimeout(self, timeout) -> None:
        """ Set a timeout between 2 updates """
        self.updateTimeout = timeout

    def ShouldUpdate(self) -> bool:
        """ Wait the correct timeout time and then the update will run """
        time.sleep(self.updateTimeout)
        return True 

    def LoopThread(self) -> None:
        """ Entry point of Entity thread, will run the Update function periodically """
        while(True):
            if self.ShouldUpdate():
                self.CallUpdate()

    def GetName(self) -> str:
        return self.name

    def Log(self, messageType, message) -> None:
        Logger.getInstance().Log(messageType, self.GetName() + " Entity", message)
        
    
    # Singleton method
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Entity.__instance == None:
            Entity()
        return Entity.__instance
