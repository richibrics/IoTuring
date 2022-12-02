import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormatter import ValueFormatter

KEY_USED_PERCENTAGE = 'space_used_percentage'


class Disk(Entity):
    NAME = "Disk"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_USED_PERCENTAGE))

    def Update(self):
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentage(
        ), ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE))

    def GetDiskUsedPercentage(self):
        return psutil.disk_usage('/')[3]
