import socket
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

KEY_HOSTNAME = 'hostname'


class Hostname(Entity):
    NAME = "Hostname"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_HOSTNAME))
        # The value for this sensor is static for the entire script run time
        self.SetEntitySensorValue(KEY_HOSTNAME, self.GetHostname())

    def GetHostname(self):
        return socket.gethostname()
