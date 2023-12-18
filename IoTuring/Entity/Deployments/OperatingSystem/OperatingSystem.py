import platform
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_OS = 'operating_system'

EXTRA_KEY_RELEASE = 'release'
EXTRA_KEY_BUILD = 'build'
EXTRA_KEY_DISTRO = 'distro'


class OperatingSystem(Entity):
    NAME = "OperatingSystem"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(
            self, KEY_OS, supportsExtraAttributes=True))

        # The value for this sensor is static for the entire script run time
        self.SetEntitySensorValue(KEY_OS, OsD.GetOs())

        extra_attrs = {}

        # win, default
        extra_attrs = {
            EXTRA_KEY_RELEASE: platform.release(),
            EXTRA_KEY_BUILD: platform.version()
        }

        if OsD.IsMacos():
            extra_attrs.update({
                EXTRA_KEY_BUILD: "".join(list(platform.mac_ver()[1]))
            })

        if OsD.IsLinux():
            if OsD.CommandExists("lsb_release"):

                extra_attrs.update({
                    EXTRA_KEY_RELEASE: self.RunCommand("lsb_release -rs").stdout,
                    EXTRA_KEY_DISTRO: self.RunCommand("lsb_release -is").stdout,
                    EXTRA_KEY_BUILD: platform.release()
                })

        for key in extra_attrs:
            self.SetEntitySensorExtraAttribute(
                KEY_OS, key, extra_attrs[key])
