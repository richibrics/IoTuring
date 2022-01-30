from Entity.EntityManager import EntityManager
from Exceptions.Exceptions import UnknownEntityKeyException
from Logger.LogObject import LogObject
from Entity.EntityData import EntitySensor, EntityCommand
import time

KEY_ENTITY_TAG = 'tag' # from Configurator.Configurator

DEFAULT_UPDATE_TIMEOUT = 10

class Entity(LogObject):
    NAME = "Unnamed"
    DEPENDENCIES = []
    ALLOW_MULTI_INSTANCE = False

    def __init__(self,configurations) -> None:
        # Prepare the entity
        self.entitySensors = [] 
        self.entityCommands = []

        self.configurations = configurations
        self.SetTagFromConfiguration()

        self.initializeState=False
        self.postinitializeState=False 
        self.valuesID = 0 # When I update the values this number changes (randomly) so each warehouse knows I have updated
        self.updateTimeout = DEFAULT_UPDATE_TIMEOUT

    def Initialize(self):
        """ Must be implemented in sub-classes, may be useful here to use the configuration """
        pass

    def CallInitialize(self): 
        """ Safe method to run the Initialize function """
        try:
            self.Initialize()
            self.initializeState=True
            self.Log(self.LOG_INFO,"Initialization successfully completed")
        except Exception as e:
            self.Log(self.LOG_ERROR,"Initialization interrupted due to an error")
            self.Log(self.LOG_ERROR,e)
            del(self)
    

    def PostInitialize(self): 
        """ Must be implemented in sub-classes """
        pass

    def CallPostInitialize(self):  
        """ Safe method to run the PostInitialize function """
        try:
            self.PostInitialize()
            self.postinitializeState=True
            self.Log(self.LOG_INFO,"Post-initialization successfully completed")
        except Exception as e:
            self.Log(self.LOG_ERROR,"Post-initialization interrupted due to an error")
            self.Log(self.LOG_ERROR,e)
            del(self)

    def CallUpdate(self):  # Call the Update method safely
        """ Safe method to run the Update function """
        try:
            self.Update()
        except Exception as exc:
            self.Log(self.LOG_ERROR, 'Error occured during update: ' + str(exc)) # TODO I need an exception manager
            # self.entityManager.UnloadEntity(self) # TODO Think how to improve this

    def Update(self):  #
        """ Must be implemented in sub-classes """
        # Can't be called directly, cause stops everything in exception, call only using CallUpdate
        pass  

    # TODO Safe to remove ?
    # def AddKey(self,key) -> None:
    #     """ Register a key so after I can assign it a value """
    #     self.Log(self.LOG_DEBUG,"Add key " + key)
    #     self.values[key]=None

    def SetEntitySensorValue(self,key,value) -> None:
        """ Set the value for an entity sensor """
        value = str(value)
        self.GetEntitySensorByKey(key).SetValue(value)

    def GetEntitySensorValue(self,key) -> str:
        """ Get value using its entity sensor key if the value is present (else raise an exception) """
        if not self.GetEntitySensorByKey(key).HasValue():
            raise Exception("The Entity sensor you asked for hasn't got a value")
        return self.GetEntitySensorByKey(key).GetValue()

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

    def RegisterEntitySensor(self, entitySensor: EntitySensor):
        self.entitySensors.append(entitySensor)

    def RegisterEntityCommand(self, entityCommand: EntityCommand):
        """ Add EntityCommand to the Entity. This action must be in Initialize or in PostInitialize, so the Waerhouses can subscribe to them at initializing time"""
        self.entityCommands.append(entityCommand)

    def GetEntitySensors(self) -> list:
        """ Return list of registered entity sensors """
        return self.entitySensors.copy() # Safe return: nobody outside can change the value !

    def GetEntityCommands(self) -> list:
        """ Return list of registered keys """
        return self.entityCommands.copy() # Safe return: nobody outside can change the callback !

    def GetEntitySensorByKey(self,key) -> EntitySensor:
        for sensor in self.entitySensors:
            if sensor.GetKey() == key:
                return sensor
        raise UnknownEntityKeyException

    def GetEntityName(self) -> str:
        return self.NAME

    @classmethod
    def GetDependenciesList(self) -> str:
        """ Static method, (safe) return the DEPENDENCIES list in the entity """
        return self.DEPENDENCIES.copy() # Safe return

    def GetDependentEntitySensorValue(self, entityToFind, dataKeyToFind):
        """ Return the value of "entityToFind"."dataKeyToFind" if it has value and I have the permission to access that entity.
            Permission is granted if "entityToFind" is present in self.GetDependenciesList() """
        
        return EntityManager.getInstance().GetDependentEntitySensorValue(self,entityToFind,dataKeyToFind)

    def GetEntityId(self)->str:
        if self.tag is not None and self.tag != "":
            return "Entity." + self.GetEntityName() +"." + self.tag
        else:
            return "Entity." + self.GetEntityName()

    def GetConfigurations(self) -> dict:
        """ Safe return entity configurations """
        if self.configurations:
            return self.configurations.copy()
        else:
            return None

    def LogSource(self):
        return self.GetEntityId()

    def SetTagFromConfiguration(self):
        """ Set tag from configuration or set it blank if not present there """
        if self.GetConfigurations() is not None and KEY_ENTITY_TAG in self.GetConfigurations():
            self.tag = self.GetConfigurations()[KEY_ENTITY_TAG]
        else: 
            self.tag = ""

    @classmethod
    def AllowMultiInstance(self):
        """ Return True if this Entity can have multiple instances, useful for customizable entities 
            These entities are the ones that must have a tag to be recognized """
        return self.ALLOW_MULTI_INSTANCE

    # Configuration methods

    @classmethod
    def ConfigurationPreset(self):
        """ Prepare a preset to manage settings insert/edit for the warehouse """
        return None