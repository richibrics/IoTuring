import uptime
from Entities.Entity import Entity


TOPIC = 'boottime'


class Boottime(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, str(uptime.boottime()))

