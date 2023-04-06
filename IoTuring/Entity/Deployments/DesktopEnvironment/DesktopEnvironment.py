from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_DE = 'desktop_environment'
EXTRA_KEY_WAYLAND = 'wayland'

# TODO Here I need the possibility for fixed value -> a configuration


class DesktopEnvironment(Entity):
    NAME = "DesktopEnvironment"

    def Initialize(self):

        # Attribute only on Linux
        self.RegisterEntitySensor(EntitySensor(
            self, KEY_DE, supportsExtraAttributes=OsD.IsLinux()))

        # The value for this sensor is static for the entire script run time
        self.SetEntitySensorValue(KEY_DE, De.GetDesktopEnvironment())

        # Add an attribute on linux checking if it's a wayland session:
        if OsD.IsLinux():
            self.SetEntitySensorExtraAttribute(
                KEY_DE, EXTRA_KEY_WAYLAND, str(De.IsWayland()))
