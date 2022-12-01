import platform
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity import consts


KEY_OS = 'operating_system'


class Os(Entity):
    NAME = "Os"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_OS))
        # The value for this sensor is static for the entire script run time (set in initialize so other entities can get the value from Postinitialize)
        self.SetEntitySensorValue(KEY_OS, self.GetOperatingSystem())

    def Update(self):
        pass

    def GetOperatingSystem(self):
        os = platform.system()
        if os == 'Darwin':  # It's macOS
            return consts.OS_FIXED_VALUE_MACOS
        elif os == "Linux":
            return consts.OS_FIXED_VALUE_LINUX
        elif os == "Windows":
            return consts.OS_FIXED_VALUE_WINDOWS
        else:
            self.Log(self.LOG_WARNING, "Operating system not in the fixed list. Please open a Git issue and warn about this: OS = \"" + os + "\"")
        return os
