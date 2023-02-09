import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormatter import ValueFormatter

KEY_USED_PERCENTAGE = 'space_used_percentage'


class Disk(Entity):
    NAME = "Disk"
    DEPENDENCIES = ["Os"]

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_USED_PERCENTAGE))

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")

    def Update(self):
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentage(
        ), ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE))

    def GetDiskUsedPercentage(self):
        if self.os == 'macOS':
            return psutil.disk_usage('/Users')[3] # macos has a different disk structure
        else:
            return psutil.disk_usage('/')[3]