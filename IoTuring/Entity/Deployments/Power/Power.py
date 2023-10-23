from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De


KEY_SHUTDOWN = 'shutdown'
KEY_REBOOT = 'reboot'
KEY_SLEEP = 'sleep'

commands_shutdown = {
    'Windows': 'shutdown /s /t 0',
    'macOS': 'sudo shutdown -h now',
    'Linux': 'poweroff'
}


commands_reboot = {
    'Windows': 'shutdown /r',
    'macOS': 'sudo reboot',
    'Linux': 'reboot'
}

commands_sleep = {
    'Windows': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
    'Linux': 'systemctl suspend',
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
        key = message.topic.split("/")[-1]
        self.RunCommand(
            command=self.commands[key],
            command_name=key
        )
