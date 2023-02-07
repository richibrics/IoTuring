import requests
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.App import App

KEY_NAME = 'name'
KEY_VERSION = 'version'
KEY_UPDATE = 'update'
PYPI_URL = 'https://pypi.org/pypi/ioturing/json'

class AppInfo(Entity):
    NAME = "AppInfo"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_NAME))
        self.RegisterEntitySensor(EntitySensor(self, KEY_VERSION))
        self.RegisterEntitySensor(EntitySensor(self, KEY_UPDATE))

    def PostInitialize(self):
        self.SetEntitySensorValue(KEY_NAME, App.getName())
        self.SetEntitySensorValue(KEY_VERSION, App.getVersion())
        if self.GetUpdateInformation():
            self.SetEntitySensorValue(
                KEY_UPDATE, True)
        else:
            self.SetEntitySensorValue(
                KEY_UPDATE, False)
        self.updateTimeout = 600

    def Update(self):
        if self.GetUpdateInformation():
            self.SetEntitySensorValue(
                KEY_UPDATE, True)
        else:
            self.SetEntitySensorValue(
                KEY_UPDATE, False)

    def GetUpdateInformation(self):
        """
        Get the update information of IoTuring
        """
        latest = ""
        res = requests.get(PYPI_URL)
        if res.status_code == 200:
            info = res.json().get("info", "")
            if len(info) >= 1:
                latest = info.get("version", "")
        current = ''.join([i for i in App.getVersion() if i.isdigit()])
        if len(latest) >= 1:
            latest = ''.join([i for i in latest if i.isdigit()])
            if int(latest) > int(current):
                return True
        return False
