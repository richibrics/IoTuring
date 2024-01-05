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

        if OsD.IsLinux():
            self.command = self.GetLinuxCommand()

        else:
            self.command = commands[OsD.GetOs()][De.GetDesktopEnvironment()]

        self.Log(self.LOG_DEBUG, f"Found lock command: {self.command}")

        self.RegisterEntityCommand(EntityCommand(
            self, KEY_LOCK, self.Callback_Lock))

    def Callback_Lock(self, message):
        self.RunCommand(command=self.command)

    @classmethod
    def GetLinuxCommand(cls) -> str:
        """ Get lock command for this DesktopEnvironment. Raises Exception if not found """
        try:
            cmd = next((commands[OsD.GetOs()][de] for de in [De.GetDesktopEnvironment(), "base"]
                        if OsD.CommandExists(commands[OsD.GetOs()][de].split()[0])))
            return cmd
        except StopIteration:
            raise Exception(f"No lock command found for this system")

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.GetOs() not in commands:
            raise cls.UnsupportedOsException()

        if OsD.IsLinux():
            try:
                cls.GetLinuxCommand()
            except Exception as e:
                raise Exception("Lock command error: " + str(e))
