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

NO_REMOTE_INSTALL_AVAILABLE_MSG = "<b>⚠️ Currently the Install process cannot be started from HomeAssistant. Please update it manually. ⚠️</b>"

UPDATE_RELEASE_SUMMARY_MAX_CHARS = 255

class AppInfo(Entity):
    NAME = "AppInfo"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_NAME, supportsExtraAttributes=True))
        self.RegisterEntitySensor(EntitySensor(self, KEY_CURRENT_VERSION, supportsExtraAttributes=True))
        self.RegisterEntitySensor(EntitySensor(self, KEY_LATEST_VERSION))
        self.RegisterEntityCommand(EntityCommand(self, KEY_UPDATE, self.InstallUpdate, [KEY_CURRENT_VERSION, KEY_LATEST_VERSION], self.UpdateCommandCustomPayload()))

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
            "release_url": App.getUrlReleases(), 
            "release_summary":  + self.getReleaseNotes()
        }

    def getReleaseNotes(self):
        release_notes = NO_REMOTE_INSTALL_AVAILABLE_MSG + "<br><ul>"
        notes = App.crawlReleaseNotes().split("\n")
        notes = ["<li>" + note + "</li>" for note in notes if len(note) > 0]
        # Sort by length
        notes.sort(key=len)
        list_end = "</ul>"
        cannot_complete_msg = "<li>...</li>"

        # Append the list to the release notes until we have space
        # If no space, append "...": take into account that we can't place a note if then the next note is too long and 
        # also there wouldn't be space for the "..."
        noteI = 0   
        end = False
        while noteI < len(notes) and not end:
            # Last note: don't need to take into account the possibility of adding "..."
            if noteI == len(notes) - 1:
                if len(release_notes) + len(notes[noteI]) + len(list_end) <= UPDATE_RELEASE_SUMMARY_MAX_CHARS:
                    release_notes += notes[noteI]
                else:
                    release_notes += cannot_complete_msg
            else: # not last note: can I add it ? If I add it, will I be able to add "..." if I won't be able to add the next note ?
                if len(release_notes) + len(notes[noteI]) + len(notes[noteI + 1]) + len(list_end) <= UPDATE_RELEASE_SUMMARY_MAX_CHARS:
                    # Both this and next note can be added -> free to add this
                    release_notes += notes[noteI]
                else: 
                    # The next note can't be added but the three dots can (and so also this note) -> Free to add this
                    if len(release_notes) + len(notes[noteI]) + len(cannot_complete_msg) + len(list_end) <= UPDATE_RELEASE_SUMMARY_MAX_CHARS:
                        release_notes += notes[noteI]
                    else:
                        # The three dots can't be added -> end
                        release_notes += cannot_complete_msg
                        end = True
            noteI += 1


        release_notes += list_end
        return release_notes

def versionToInt(version: str):
    return int(''.join([i for i in version if i.isdigit()]))
    
class UpdateCheckException(Exception):
    pass