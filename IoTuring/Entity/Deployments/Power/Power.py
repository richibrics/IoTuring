from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.Exceptions.Exceptions import UnknownConfigKeyException
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De
from IoTuring.Configurator.MenuPreset import MenuPreset


CONFIG_KEY_ENABLE_HIBERNATE = 'enable_hibernate'

KEY_SHUTDOWN = 'shutdown'
KEY_REBOOT = 'reboot'
KEY_SLEEP = 'sleep'
KEY_HIBERNATE = 'hibernate'

commands = {
    OsD.WINDOWS: {
        KEY_SHUTDOWN: 'shutdown /s /t 0',
        KEY_REBOOT: 'shutdown /r',
        KEY_SLEEP: 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
        KEY_HIBERNATE: 'rundll32.exe powrprof.dll,SetSuspendState Hibernate'

    },
    OsD.MACOS: {
        KEY_SHUTDOWN: 'sudo shutdown -h now',
        KEY_REBOOT: 'sudo reboot'
    },
    OsD.LINUX: {
        KEY_SHUTDOWN: 'poweroff',
        KEY_REBOOT: 'reboot',
        KEY_SLEEP: 'systemctl suspend',
        KEY_HIBERNATE: 'systemctl hibernate'
    }
}

linux_commands = {
    "gnome": {
        KEY_SHUTDOWN: 'gnome-session-quit --power-off',
        KEY_REBOOT: 'gnome-session-quit --reboot'
    },
    "X11": {
        KEY_SLEEP: 'xset dpms force standby'
    }
}


class Power(Entity):
    NAME = "Power"

    def Initialize(self):
        self.commands = {}

        command_keys = [KEY_SHUTDOWN, KEY_REBOOT, KEY_SLEEP]

        try:
            if self.GetTrueOrFalseFromConfigurations(CONFIG_KEY_ENABLE_HIBERNATE):
                command_keys.append(KEY_HIBERNATE)
        except UnknownConfigKeyException:
            pass

        for command_key in command_keys:
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

            if De.IsXsetSupported() and command_key in linux_commands['X11']:
                command = linux_commands['X11'][command_key]
            elif De.GetDesktopEnvironment() in linux_commands \
                    and command_key in linux_commands[De.GetDesktopEnvironment()]:
                command = linux_commands[De.GetDesktopEnvironment(
                )][command_key]

            elif not command.startswith("systemctl"):
                # Try if command works without sudo, add if it's not working:
                testcommand = command + " --wtmp-only"

                if not self.RunCommand(testcommand).returncode == 0:
                    command = "sudo " + command

        self.Log(self.LOG_DEBUG,
                 f'Found {command_key} command: {command}')

        return command

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()

        if KEY_HIBERNATE in commands[OsD.GetOs()]:
            preset.AddEntry("Enable hibernation",
                            CONFIG_KEY_ENABLE_HIBERNATE, default="N",
                            question_type="yesno")
        return preset

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.GetOs() not in commands:
            raise cls.UnsupportedOsException()
