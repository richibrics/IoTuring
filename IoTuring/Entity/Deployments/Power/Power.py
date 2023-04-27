import subprocess
import os as sys_os
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD # don't name Os as could be a problem with old configurations that used the Os entity


KEY_SHUTDOWN = 'shutdown'
KEY_REBOOT = 'reboot'
KEY_SLEEP = 'sleep'

commands_shutdown = {
    'Windows': 'shutdown /s /t 0',
    'macOS': 'sudo shutdown -h now',
    'Linux': 'sudo shutdown -h now'
}

commands_reboot = {
    'Windows': 'shutdown /r',
    'macOS': 'sudo reboot',
    'Linux': 'sudo reboot'
}

commands_sleep = {
    'Windows': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
    'Linux_X11': 'xset dpms force standby'
}


class Power(Entity):
    NAME = "Power"

    def Initialize(self):
        self.sleep_command = ""

        self.os = OsD.GetOs()
        # Check if commands are available for this OS/DE combo, then register them

        # Shutdown
        if self.os in commands_shutdown:
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_SHUTDOWN, self.CallbackShutdown))

        # Reboot
        if self.os in commands_reboot:
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_REBOOT, self.CallbackReboot))

        # Sleep
        # TODO Update TurnOffMonitors, TurnOnMonitors, LockCommand to use prefix lookup below
        # Additional linux checking to find Window Manager: check running X11 for linux
        prefix = ''
        if OsD.IsLinux() and sys_os.environ.get('DISPLAY'):
            prefix = '_X11'
        lookup_key = self.os + prefix
        if lookup_key in commands_sleep:
            self.sleep_command = commands_sleep[lookup_key]
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_SLEEP, self.CallbackSleep))

    def CallbackShutdown(self, message):
        subprocess.Popen(
            commands_shutdown[self.os].split(), stdout=subprocess.PIPE)

    def CallbackReboot(self, message):
        subprocess.Popen(
            commands_reboot[self.os].split(), stdout=subprocess.PIPE)

    def CallbackSleep(self, message):
        subprocess.Popen(self.sleep_command.split(), stdout=subprocess.PIPE)
