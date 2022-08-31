import uptime
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor
from Entity.ValueFormatter import ValueFormatter 

KEY = 'uptime'

class Uptime(Entity):
    NAME = "UpTime"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY))

    def Update(self):
        self.SetEntitySensorValue(KEY, uptime.uptime(), ValueFormatter.Options(ValueFormatter.TYPE_TIME, 0, "m"))