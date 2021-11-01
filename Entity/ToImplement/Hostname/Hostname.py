import socket
from Entities.Entity import Entity


TOPIC = 'hostname'


class Hostname(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, str(self.GetHostname()))

    def GetHostname(self):
      return socket.gethostname()


