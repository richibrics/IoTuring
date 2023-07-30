import subprocess
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD # don't name Os as could be a problem with old configurations that used the Os entity

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
        'i3': 'i3lock',
        'plasma': 'loginctl lock-session'
    }
}


class Lock(Entity):
    NAME = "Lock"

    def Initialize(self):
        self.RegisterEntityCommand(EntityCommand(
            self, KEY_LOCK, self.Callback_Lock))

        self.os = OsD.GetOs()
        self.de = De.GetDesktopEnvironment()

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
