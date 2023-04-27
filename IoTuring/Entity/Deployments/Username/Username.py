import os
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

KEY_USERNAME = "username"


class Username(Entity):
    NAME = "Username"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_USERNAME))
        self.SetEntitySensorValue(KEY_USERNAME, self.GetUsername())


    def GetUsername(self):
        # Gives user's home directory
        userhome = os.path.expanduser('~')

        # Gives username by splitting path based on OS
        return os.path.split(userhome)[-1]
