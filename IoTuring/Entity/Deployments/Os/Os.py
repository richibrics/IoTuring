import platform
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.SystemConsts.SystemConsts import Os

KEY_OS = 'operating_system'


class OperatingSystem(Entity):
    NAME = "OperatingSystem"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_OS))
        # The value for this sensor is static for the entire script run time (set in initialize so other entities can get the value from Postinitialize)
        self.SetEntitySensorValue(KEY_OS, Os.GetOs())

    def Update(self):
        pass
