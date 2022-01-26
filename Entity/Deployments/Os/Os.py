import platform
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor

FIXED_VALUE_OS_MACOS = "macOS"

KEY_OS = 'operating_system'

class Os(Entity):
    name = "Os"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self,KEY_OS))
 
    def PostInitialize(self):
        # The value for this sensor is static for the entire script run time
        self.SetEntitySensorValue(KEY_OS,self.GetOperatingSystem())
        
    def Update(self):
        pass

    def GetOperatingSystem(self):
        os = platform.system()
        if os == 'Darwin':  # It's macOS
            return FIXED_VALUE_OS_MACOS
        return os
