import imp
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor 
from MyApp.App import App

KEY_NAME = 'name'
KEY_VERSION = 'version'

class AppInfo(Entity):
    NAME = "AppInfo"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self,KEY_NAME))
        self.RegisterEntitySensor(EntitySensor(self,KEY_VERSION))

    def PostInitialize(self):
        self.SetEntitySensorValue(KEY_NAME, App.getName())
        self.SetEntitySensorValue(KEY_VERSION, App.getVersion())

    def Update(self):
        pass