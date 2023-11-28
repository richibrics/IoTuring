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

        if OsD.IsLinux():
            if De.IsWayland():
                raise Exception("Wayland is not supported")
            else:
                try:
                    De.CheckXsetSupport()
                except Exception as e:
                    raise Exception(f'Xset not supported: {str(e)}')

                self.RegisterEntitySensor(EntitySensor(self, KEY_STATE))
                self.RegisterEntityCommand(EntityCommand(
                    self, KEY_CMD, self.Callback, KEY_STATE))

        elif OsD.IsWindows():
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.Callback))

        else:
            raise Exception("Operating System not supported!")

    def Callback(self, message):
        payloadString = message.payload.decode('utf-8')

        if payloadString == STATE_ON:
            if OsD.IsWindows():
                ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, -1) # type:ignore
            elif OsD.IsLinux():
                self.RunCommand(command='xset dpms force on')

        elif payloadString == STATE_OFF:
            if OsD.IsWindows():
                ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, 2) # type:ignore
            elif OsD.IsLinux():
                self.RunCommand(command='xset dpms force off')
        else:
            raise Exception('Incorrect payload!')

    def Update(self):
        if OsD.IsLinux():
            p = self.RunCommand(command="xset q")
            monitorState = re.findall(
                'Monitor is (.{2,3})', p.stdout)[0].upper()
            if monitorState in [STATE_OFF, STATE_ON]:
                self.SetEntitySensorValue(KEY_STATE, monitorState)
            else:
                raise Exception(f'Incorrect monitor state: {monitorState}')
