import psutil
import time
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions

KEY = 'uptime'


class Uptime(Entity):
    NAME = "UpTime"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY, valueFormatterOptions=ValueFormatterOptions(ValueFormatterOptions.TYPE_TIME, 0, "m")))

    def Update(self):
        self.SetEntitySensorValue(KEY, time.time() - psutil.boot_time())
