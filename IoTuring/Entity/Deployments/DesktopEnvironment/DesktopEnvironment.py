import os
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De

KEY_DE = 'desktop_environment'

# TODO Here I need the possibility for fixed value -> a configuration

class DesktopEnvironment(Entity):
    NAME = "DesktopEnvironment"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_DE))
        # The value for this sensor is static for the entire script run time (set in initialize so other entities can get the value from Postinitialize)
        self.SetEntitySensorValue(KEY_DE, De.GetDesktopEnvironment())