from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De


KEY_SHUTDOWN = 'shutdown'
KEY_REBOOT = 'reboot'
KEY_SLEEP = 'sleep'

commands_shutdown = {
    OsD.WINDOWS: 'shutdown /s /t 0',
    OsD.MACOS: 'sudo shutdown -h now',
    OsD.LINUX: 'poweroff'
}


commands_reboot = {
    OsD.WINDOWS: 'shutdown /r',
    OsD.MACOS: 'sudo reboot',
    OsD.LINUX: 'reboot'
}

commands_sleep = {
    OsD.WINDOWS: 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
    OsD.LINUX: 'systemctl suspend',
    'Linux_X11': 'xset dpms force standby',
}


class Power(Entity):
    NAME = "Power"

    def Initialize(self):
        self.commands = {}

        self.os = OsD.GetOs()
        # Check if commands are available for this OS/DE combo, then register them

        # Shutdown
        if self.os in commands_shutdown:
            self.commands[KEY_SHUTDOWN] = commands_shutdown[self.os]
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_SHUTDOWN, self.Callback))

        # Reboot
        if self.os in commands_reboot:
            self.commands[KEY_REBOOT] = commands_reboot[self.os]
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_REBOOT, self.Callback))

        # Try if command works without sudo, add if it's not working:
        if OsD.IsLinux():
            for commandtype in self.commands:
                testcommand = self.commands[commandtype] + " --wtmp-only"
                if not self.RunCommand(testcommand).returncode == 0:
                    self.commands[commandtype] = "sudo " + \
                        self.commands[commandtype]

        # Sleep
        if self.os in commands_sleep:
            self.commands[KEY_SLEEP] = commands_sleep[self.os]

            # Fallback to xset, if supported:
            if OsD.IsLinux() and not De.IsWayland():
                try:
                    De.CheckXsetSupport()
                    self.commands[KEY_SLEEP] = commands_sleep["Linux_X11"]
                except Exception as e:
                    self.Log(self.LOG_DEBUG, f'Xset not supported: {str(e)}')

            self.RegisterEntityCommand(EntityCommand(
                self, KEY_SLEEP, self.Callback))

    def Callback(self, message):
        # From the topic we can find the command:
        key = message.topic.split("/")[-1]
        self.RunCommand(
            command=self.commands[key],
            command_name=key
        )
