import subprocess
import ctypes
import re

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De


KEY_STATE = 'monitor_state'
KEY_CMD = 'monitor'

class Monitor(Entity):
    NAME = "Monitor"

    def Initialize(self):
        supports_linux = False
        if OsD.IsLinux():
            if De.IsWayland():
                raise Exception("Wayland is not supported")
            elif not OsD.CommandExists("xset"):
                raise Exception("xset command not found!")
            else:
                # Check if xset is working:
                p = subprocess.run(['xset', 'dpms'], capture_output=True, shell=False)
                if p.stderr:
                    raise Exception(f"Xset dpms error: {p.stderr.decode()}")
                elif not OsD.GetEnv('DISPLAY'):
                    raise Exception('No $DISPLAY environment variable!')
                else:
                    supports_linux = True

        if OsD.IsWindows():
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.Callback))
        elif supports_linux: # True only if linux and command is working
            # Support for sending state on linux
            self.RegisterEntitySensor(EntitySensor(self, KEY_STATE))
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.Callback, KEY_STATE))

    def Callback(self, message):
        payloadString = message.payload.decode('utf-8')

        if payloadString == STATE_ON:
            if OsD.IsWindows():
                ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, -1)
            elif OsD.IsLinux():
                command = 'xset dpms force on'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)

        elif payloadString == STATE_OFF:
            if OsD.IsWindows():
                ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, 2)
            elif OsD.IsLinux():
                command = 'xset dpms force off'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        else:
            raise Exception('Incorrect payload!')

    def Update(self):
        if OsD.IsLinux():
            p = subprocess.run(['xset', 'q'], capture_output=True, shell=False)
            outputString = p.stdout.decode()
            monitorState = re.findall(
                'Monitor is (.{2,3})', outputString)[0].upper()
            if monitorState in [STATE_OFF, STATE_ON]:
                self.SetEntitySensorValue(KEY_STATE, monitorState)
            else:
                raise Exception(f'Incorrect monitor state: {monitorState}')
