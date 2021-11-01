import os
from Entities.Entity import Entity


TOPIC = 'username'


class Username(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, str(self.GetUsername()))

    def GetUsername(self):
        # Gives user's home directory
        userhome = os.path.expanduser('~')

        # Gives username by splitting path based on OS
        return os.path.split(userhome)[-1] 

