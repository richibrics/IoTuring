import uptime
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor 

KEY_BOOT_TIME = 'boot_time'

class BootTime(Entity):
    NAME = "BootTime"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self,KEY_BOOT_TIME))

    def Update(self):
        self.SetEntitySensorValue(KEY_BOOT_TIME, str(uptime.boottime().strftime("%Y-%m-%d %H:%M:%S")))