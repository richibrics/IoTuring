from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_LOCK = 'lock'

commands = {
    OsD.WINDOWS: {
        'base': 'rundll32.exe user32.dll,LockWorkStation'
    },
    OsD.MACOS: {
        'base': 'pmset displaysleepnow'
    },
    OsD.LINUX: {
        'gnome': 'gnome-screensaver-command -l',
        'cinnamon': 'cinnamon-screensaver-command -a',
        'i3': 'i3lock',
        'base': 'loginctl lock-session'
    }
}


class Lock(Entity):
    NAME = "Lock"

    def Initialize(self):
        self.os = OsD.GetOs()
        self.de = De.GetDesktopEnvironment()

        if self.os not in commands:
            raise Exception("Unsupported operating system for this entity")

        # Fallback to base, if unsupported de:
        if self.de == "base" or self.de not in commands[self.os]:
            desktops = ["base"]

        # supported de, add base as fallback:
        else:
            desktops = [self.de, "base"]

        # Check if command works:
        try:
            self.command = next((commands[self.os][de] for de in desktops
                                 if OsD.CommandExists(commands[self.os][de].split()[0])))

        except StopIteration:
            raise Exception(f"No lock command found for this system")

        self.Log(self.LOG_DEBUG, f"Found lock command: {self.command}")

        self.RegisterEntityCommand(EntityCommand(
            self, KEY_LOCK, self.Callback_Lock))

    def Callback_Lock(self, message):
        self.RunCommand(command=self.command)
