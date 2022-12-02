import datetime
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

KEY_NOW = 'now'


class Time(Entity):
    NAME = "Time"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_NOW))

    def Update(self):
        self.SetEntitySensorValue(KEY_NOW, self.GetCurrentTime())

    def GetCurrentTime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
