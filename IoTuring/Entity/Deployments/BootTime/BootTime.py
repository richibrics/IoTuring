import datetime
import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

KEY_BOOT_TIME = 'boot_time'


class BootTime(Entity):
    NAME = "BootTime"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_BOOT_TIME))

    def Update(self):
        self.SetEntitySensorValue(KEY_BOOT_TIME,
                                  str(datetime.datetime.fromtimestamp(psutil.boot_time())))
