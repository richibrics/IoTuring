import psutil
from Entities.Entity import Entity


TOPIC = 'disk_used_percentage'


class Disk(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, self.GetDiskUsedPercentage(),self.ValueFormatter.TYPE_PERCENTAGE)

    def GetDiskUsedPercentage(self):
        return psutil.disk_usage('/')[3]
