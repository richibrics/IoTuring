import requests
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.MyApp.App import App

KEY_NAME = 'name'
KEY_CURRENT_VERSION = 'current_version'
KEY_LATEST_VERSION = 'latest_version'
KEY_UPDATE = 'update'

PYPI_URL = 'https://pypi.org/pypi/ioturing/json'

GET_UPDATE_ERROR_MESSAGE = "Error while checking, try to update to solve this problem. Alert the developers if the problem persists."

EXTRA_ATTRIBUTE_UPDATE_ERROR = 'Check error'

class AppInfo(Entity):
    NAME = "AppInfo"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_NAME, supportsExtraAttributes=True))
        self.RegisterEntitySensor(EntitySensor(self, KEY_CURRENT_VERSION))
        self.RegisterEntitySensor(EntitySensor(self, KEY_LATEST_VERSION, supportsExtraAttributes=True))
        self.RegisterEntityCommand(EntityCommand(self, KEY_UPDATE, self.InstallUpdate, KEY_CURRENT_VERSION, [KEY_LATEST_VERSION], self.UpdateCommandCustomPayload()))

        self.SetEntitySensorValue(KEY_NAME, App.getName())
        self.SetEntitySensorValue(KEY_CURRENT_VERSION, App.getVersion())
        self.SetUpdateTimeout(600)

    def InstallUpdate(self, message):
        raise NotImplementedError("InstallUpdate not implemented")

    def Update(self):
        # VERSION UPDATE CHECK
        try:
            new_version = self.GetUpdateInformation()
            
            if not new_version: # signal no update and current version (as its the latest)
                self.SetEntitySensorValue(KEY_LATEST_VERSION, App.getVersion())
            else: # signal update and latest version
                self.SetEntitySensorValue(KEY_LATEST_VERSION, new_version)
        except Exception as e:
            # connection error or pypi name changed or something else
            # add extra attribute to show error message
            self.SetEntitySensorExtraAttribute(KEY_CURRENT_VERSION, EXTRA_ATTRIBUTE_UPDATE_ERROR, GET_UPDATE_ERROR_MESSAGE)
            

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
            else:
                raise UpdateCheckException()
        else: 
            raise UpdateCheckException()
        if len(latest) >= 1:
            if versionToInt(latest) > versionToInt(App.getVersion()):
                return latest
            else:
                return False
        else:
            raise UpdateCheckException()
    
    def UpdateCommandCustomPayload(self):
        return {
            "title": App.getName(),
            "name": App.getName(),
            "release_url": App.getUrlReleases()
        }

def versionToInt(version: str):
    return int(''.join([i for i in version if i.isdigit()]))
    
class UpdateCheckException(Exception):
    pass