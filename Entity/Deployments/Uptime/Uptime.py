import psutil
import time
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor
from Entity.ValueFormatter import ValueFormatter

KEY = 'uptime'


class Uptime(Entity):
    NAME = "UpTime"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY))

    def Update(self):
        self.SetEntitySensorValue(KEY, time.time() - psutil.boot_time(),
                                  ValueFormatter.Options(ValueFormatter.TYPE_TIME, 0, "m"))
