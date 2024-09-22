from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from IoTuring.Configurator.Configuration import SingleConfiguration
    from IoTuring.Entity.EntityData import EntityData, EntitySensor, EntityCommand, ExtraAttribute


import time
import subprocess

from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Logger.LogObject import LogObject
from IoTuring.Exceptions.Exceptions import UnknownEntityKeyException

from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

from IoTuring.Settings.Deployments.AppSettings.AppSettings import AppSettings, CONFIG_KEY_UPDATE_INTERVAL


class Entity(ConfiguratorObject, LogObject):

    entitySensors: list[EntitySensor]
    entityCommands: list[EntityCommand]

    def __init__(self, single_configuration: SingleConfiguration) -> None:
        super().__init__(single_configuration)

        # Prepare the entity
        self.entitySensors = []
        self.entityCommands = []

        self.tag = self.GetConfigurations().GetTag()

        # When I update the values this number changes (randomly) so each warehouse knows I have updated
        self.valuesID = 0

        self.updateTimeout = int(
            AppSettings.GetFromSettingsConfigurations(CONFIG_KEY_UPDATE_INTERVAL))

    def Initialize(self):
        """ Must be implemented in sub-classes, may be useful here to use the configuration """
        pass

    def CallInitialize(self) -> bool:
        """ Safe method to run the Initialize function. Returns True if no error occcured. """
        try:
            self.CheckSystemSupport()
            self.Initialize()
            self.Log(self.LOG_INFO, "Initialization successfully completed")
        except Exception as e:
            self.Log(self.LOG_ERROR,
                     "Initialization interrupted due to an error:")
            self.Log(self.LOG_ERROR, e)
            return False
        return True

    def CallUpdate(self):  # Call the Update method safely
        """ Safe method to run the Update function """
        try:
            self.Update()
        except Exception as exc:
            # TODO I need an exception manager
            self.Log(self.LOG_ERROR, 'Error occured during update: ' + str(exc))
            #  self.entityManager.UnloadEntity(self) # TODO Think how to improve this

    def Update(self):
        """ Must be implemented in sub-classes """
        # Can't be called directly, cause stops everything in exception, call only using CallUpdate
        pass

    def SetEntitySensorValue(self, key, value) -> None:
        """ Set the value for an entity sensor """
        self.GetEntitySensorByKey(key).SetValue(value)

    def GetEntitySensorValue(self, key) -> str | int | float:
        """ Get value using its entity sensor key if the value is present (else raise an exception) """
        if not self.GetEntitySensorByKey(key).HasValue():
            raise Exception(
                "The Entity sensor you asked for hasn't got a value")
        return self.GetEntitySensorByKey(key).GetValue()

    def HasEntitySensorExtraAttributes(self, key) -> bool:
        """ Check if EntitySensor has an extra attributes dict """
        return self.GetEntitySensorByKey(key).HasExtraAttributes()

    def GetEntitySensorExtraAttributes(self, key) -> list[ExtraAttribute]:
        """ Get attributes using its entity sensor key if the extra attributes are present (else raise an exception) """
        if not self.GetEntitySensorByKey(key).HasExtraAttributes():
            raise Exception(
                "The Entity sensor you asked for hasn't got extra attributes")
        return self.GetEntitySensorByKey(key).GetExtraAttributes()

    def SetEntitySensorExtraAttribute(self, sensorDataKey, attributeKey, attributeValue, valueFormatterOptions=None) -> None:
        """ Set the extra attribute for an entity sensor """
        self.GetEntitySensorByKey(sensorDataKey).SetExtraAttribute(
            attributeKey, attributeValue, valueFormatterOptions)

    def SetUpdateTimeout(self, timeout) -> None:
        """ Set how much time to wait between 2 updates """
        self.updateTimeout = timeout

    def ShouldUpdate(self) -> bool:
        """ Wait the correct timeout time and then the update will run """
        time.sleep(self.updateTimeout)
        return True

    def LoopThread(self) -> None:
        """ Entry point of Entity thread, will run the Update function periodically """
        self.CallUpdate()  # first call
        while (True):
            if self.ShouldUpdate():
                self.CallUpdate()

    def RegisterEntitySensor(self, entitySensor: EntitySensor):
        """ Add EntitySensor to the Entity. This action must be in Initialize """
        self.entitySensors.append(entitySensor)

    def RegisterEntityCommand(self, entityCommand: EntityCommand):
        """ Add EntityCommand to the Entity. This action must be in Initialize, so the Warehouses can subscribe to them at initializing time"""
        self.entityCommands.append(entityCommand)

    def GetEntitySensors(self) -> list[EntitySensor]:
        """ safe - Return list of registered entity sensors """
        return self.entitySensors.copy()  # Safe return: nobody outside can change the value !

    def GetEntityCommands(self) -> list[EntityCommand]:
        """ safe - Return list of registered entity commands """
        return self.entityCommands.copy()  # Safe return: nobody outside can change the callback !

    def GetAllEntityData(self) -> list:
        """ safe - Return list of entity sensors and commands """
        return self.entityCommands.copy() + self.entitySensors.copy()  # Safe return: nobody outside can change the callback !

    def GetAllUnconnectedEntityData(self) -> list[EntityCommand|EntitySensor]:
        """ safe - Return All EntityCommands and EntitySensors without connected sensors """
        connected_sensors = []
        for command in self.entityCommands:
            connected_sensors.extend(command.GetConnectedEntitySensors())
        
        unconnected_sensors = [sensor for sensor in self.entitySensors
                               if sensor not in connected_sensors]
        return self.entityCommands.copy() + unconnected_sensors.copy()

    def GetEntitySensorByKey(self, key) -> EntitySensor:
        try:
            sensor = next((s for s in self.entitySensors if s.GetKey() == key))
            return sensor
        except StopIteration:
            raise UnknownEntityKeyException(key)

    def GetEntityName(self) -> str:
        """ Return entity name """
        return self.NAME

    def GetEntityTag(self) -> str:
        """ Return entity identifier tag """
        return self.tag

    def GetEntityNameWithTag(self) -> str:
        """ Return entity name and tag combined (or name alone if no tag is present) """
        if self.tag:
            return self.GetEntityName()+" @" + self.GetEntityTag()
        else:
            return self.GetEntityName()

    def GetEntityId(self) -> str:
        if self.tag:
            return "Entity." + self.GetEntityName() + "." + self.tag
        else:
            return "Entity." + self.GetEntityName()

    def LogSource(self):
        return self.GetEntityId()

    def RunCommand(self,
                   command: str | list,
                   command_name: str = "",
                   log_errors: bool = True,
                   shell: bool = False,
                   **kwargs) -> subprocess.CompletedProcess:
        """Safely call a subprocess. Kwargs are other Subprocess options

        Args:
            command (str | list): The command to call
            command_name (str, optional): For logging, if empty entity name will be used.
            log_errors (bool, optional): Log stderr of command. Use False when failure is expected. Defaults to True.
            shell (bool, optional): Run in shell. Defaults to False.
            **kwargs: subprocess args

        Returns:
            subprocess.CompletedProcess: See subprocess docs
        """

        try:

            if command_name:
                command_name = self.NAME + "-" + command_name
            else:
                command_name = self.NAME

            p = OsD.RunCommand(command, shell=shell, **kwargs)

            self.Log(self.LOG_DEBUG, f"Called {command_name} command: {p}")

            # Do not log errors:
            error_loglevel = self.LOG_ERROR if log_errors else self.LOG_DEBUG
            if p.stderr:
                self.Log(error_loglevel,
                         f"Error during {command_name} command: {p.stderr}")
            
            return p

        except Exception as e:
            raise Exception(f"Error during {command_name} command: {str(e)}")


    @classmethod
    def CheckSystemSupport(cls):
        """Must be implemented in subclasses. Raise an exception if system not supported."""
        return

    @classmethod
    def SystemSupported(cls) -> bool:
        """Check if the sysytem supported by this entity.

        Returns:
            bool: True if supported
        """
        try:
            cls.CheckSystemSupport()
            return True
        except:
            return False

    class UnsupportedOsException(Exception):
        def __init__(self) -> None:
            super().__init__(f"Unsupported operating system: {OsD.GetOs()}")
