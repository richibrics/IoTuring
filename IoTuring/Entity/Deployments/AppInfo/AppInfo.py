import requests
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.App import App

KEY_NAME = 'name'
KEY_VERSION = 'version'
KEY_UPDATE = 'update'
PYPI_URL = 'https://pypi.org/pypi/ioturing/json'

EXTRA_ATTRIBUTE_LATEST = 'Latest version'

class AppInfo(Entity):
    NAME = "AppInfo"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_NAME))
        self.RegisterEntitySensor(EntitySensor(self, KEY_VERSION))
        self.RegisterEntitySensor(EntitySensor(self, KEY_UPDATE, supportsExtraAttributes=True))

    def PostInitialize(self):
        self.SetEntitySensorValue(KEY_NAME, App.getName())
        self.SetEntitySensorValue(KEY_VERSION, App.getVersion())
        self.SetUpdateTimeout(600)

    def Update(self):
        # VERSION UPDATE CHECK
        new_version = self.GetUpdateInformation()
        if not new_version:
            self.SetEntitySensorValue(
                KEY_UPDATE, False)
            self.SetEntitySensorExtraAttributes(KEY_UPDATE, {EXTRA_ATTRIBUTE_LATEST: App.getVersion()})
        else:
            self.SetEntitySensorValue(
                KEY_UPDATE, True)
            self.SetEntitySensorExtraAttributes(KEY_UPDATE, {EXTRA_ATTRIBUTE_LATEST: new_version})

    def GetUpdateInformation(self):
        """
        Get the update information of IoTuring
        Returns False if no update is available
        Otherwise returns the latest version (could be set as extra attribute)
        """
        latest = ""
        res = requests.get(PYPI_URL)
        if res.status_code == 200:
            info = res.json().get("info", "")
            if len(info) >= 1:
                latest = info.get("version", "")
        if len(latest) >= 1:
            if versionToInt(latest) > versionToInt(App.getVersion()):
                return latest
        return False
    
def versionToInt(version: str):
    return int(''.join([i for i in version if i.isdigit()]))
    
