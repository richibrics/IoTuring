import uptime
from Entity.Entity import Entity 


TOPIC = 'boottime'


class Boottime(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, str(uptime.boottime()))

