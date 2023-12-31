from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De


KEY_SHUTDOWN = 'shutdown'
KEY_REBOOT = 'reboot'
KEY_SLEEP = 'sleep'

commands = {
    OsD.WINDOWS: {
        KEY_SHUTDOWN: 'shutdown /s /t 0',
        KEY_REBOOT: 'shutdown /r',
        KEY_SLEEP: 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'
    },
    OsD.MACOS: {
        KEY_SHUTDOWN: 'sudo shutdown -h now',
        KEY_REBOOT: 'sudo reboot'
    },
    OsD.LINUX: {
        KEY_SHUTDOWN: 'poweroff',
        KEY_REBOOT: 'reboot',
        KEY_SLEEP: 'systemctl suspend'
    }
}

linux_optional_sleep_commands = {
    'X11': 'xset dpms force standby'
}


class Power(Entity):
    NAME = "Power"

    def Initialize(self):
        self.commands = {}

        for command_key in [KEY_SHUTDOWN, KEY_REBOOT, KEY_SLEEP]:
            if command_key in commands[OsD.GetOs()]:
                self.commands[command_key] = self.GetCommand(command_key)
                self.RegisterEntityCommand(EntityCommand(
                    self, command_key, self.Callback))

    def Callback(self, message):
        # From the topic we can find the command:
        key = message.topic.split("/")[-1]
        self.RunCommand(
            command=self.commands[key],
            command_name=key
        )

    def GetCommand(self, command_key: str) -> str:
        """Get the command for this command_key

        Args:
            command_key (str): KEY_SHUTDOWN, KEY_REBOOT or KEY_SLEEP

        Returns:
            str: The command string
        """

        command = commands[OsD.GetOs()][command_key]

        if OsD.IsLinux():

            if command_key == KEY_SLEEP:
                # Fallback to xset, if supported:
                if not De.IsWayland():
                    try:
                        De.CheckXsetSupport()
                        command = linux_optional_sleep_commands['X11']
                    except Exception as e:
                        self.Log(self.LOG_DEBUG,
                                 f'Xset not supported: {str(e)}')

            else:
                # Try if command works without sudo, add if it's not working:
                testcommand = command + " --wtmp-only"

                if not self.RunCommand(testcommand).returncode == 0:
                    command = "sudo " + command

        self.Log(self.LOG_DEBUG,
                 f'Found {command_key} command: {command}')

        return command

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.GetOs() not in commands:
            raise cls.UnsupportedOsException()
