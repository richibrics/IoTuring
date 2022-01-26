import uptime
from Entity.Entity import Entity 

TOPIC = 'uptime'

class Uptime(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, str(uptime.uptime()))

