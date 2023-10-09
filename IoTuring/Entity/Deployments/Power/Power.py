import subprocess

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
                self, KEY_SHUTDOWN, self.CallbackShutdown))

        # Reboot
        if self.os in commands_reboot:
            self.commands[KEY_REBOOT] = commands_reboot[self.os]
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_REBOOT, self.CallbackReboot))

        # Try if command works without sudo, add if it's not working:
        if OsD.IsLinux():
            for commandtype in self.commands:
                testcommand = self.commands[commandtype] + " --wtmp-only"
                if not subprocess.run(testcommand.split(), capture_output=True).returncode == 0:
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
                self, KEY_SLEEP, self.CallbackSleep))

    def CallCommand(self, command_key: str) -> None:
        # Log if a command not working:
        try:
            p = subprocess.run(
                self.commands[command_key].split(), capture_output=True)
            self.Log(self.LOG_DEBUG, f"Called {command_key} command: {p}")

            if p.stderr:
                self.Log(self.LOG_ERROR,
                         f"Error during system {command_key}: {p.stderr}")

        except Exception as e:
            raise Exception(f'Error during system {command_key}: {str(e)}')

    def CallbackShutdown(self, message):
        self.CallCommand(KEY_SHUTDOWN)

    def CallbackReboot(self, message):
        self.CallCommand(KEY_REBOOT)

    def CallbackSleep(self, message):
        self.CallCommand(KEY_SLEEP)
