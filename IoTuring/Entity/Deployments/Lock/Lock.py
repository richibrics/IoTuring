import subprocess
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand

KEY_LOCK = 'lock'

commands = {
    'Windows': {
        'base': 'rundll32.exe user32.dll,LockWorkStation'
    },
    'macOS': {
        'base': 'pmset displaysleepnow'
    },
    'Linux': {
        'gnome': 'gnome-screensaver-command -l',
        'cinnamon': 'cinnamon-screensaver-command -a',
        'i3': 'i3lock'
    }
}


class Lock(Entity):
    NAME = "Lock"
    DEPENDENCIES = ["Os", "DesktopEnvironment"]

    def Initialize(self):
        self.RegisterEntityCommand(EntityCommand(
            self, KEY_LOCK, self.Callback_Lock))

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")
        self.de = self.GetDependentEntitySensorValue(
            'DesktopEnvironment', 'desktop_environment')

    def Callback_Lock(self, message):
        if self.os in commands:
            if self.de in commands[self.os]:
                try:
                    command = commands[self.os][self.de]
                    process = subprocess.Popen(
                        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:
                    raise Exception('Error during system lock: ' + str(e))
            else:
                raise Exception(
                    'No lock command for this Desktop Environment: ' + self.de)
        else:
            raise Exception(
                'No lock command for this Operating System: ' + self.os)
