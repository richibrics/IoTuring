import platform
import subprocess
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
# don't name Os as could be a problem with old configurations that used the Os entity:
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
                p_release = subprocess.run(['lsb_release', '-rs'],
                                   capture_output=True, shell=False)
                p_id = subprocess.run(['lsb_release', '-is'],
                                   capture_output=True, shell=False)

                extra_attrs.update({
                    EXTRA_KEY_RELEASE: p_release.stdout.decode().strip(),
                    EXTRA_KEY_DISTRO: p_id.stdout.decode().strip(),
                    EXTRA_KEY_BUILD: platform.release()
                })

        for key in extra_attrs:
            self.SetEntitySensorExtraAttribute(
                KEY_OS, key, extra_attrs[key])
