import subprocess
import ctypes
import os as sys_os
from IoTuring.Entity.Entity import Entity
from ctypes import *

from IoTuring.Entity.EntityData import EntityCommand

KEY_TURN_ALL_OFF = 'turn_all_off'
KEY_TURN_ALL_ON = 'turn_all_on'


class Monitor(Entity):
    NAME = "Monitor"

    def Initialize(self):
        pass

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")

        if self.os == 'Windows' or (self.os == 'Linux' and sys_os.environ.get('DISPLAY')):
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_TURN_ALL_OFF, self.CallbackTurnAllOff))
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_TURN_ALL_ON, self.CallbackTurnAllOn))

    def CallbackTurnAllOff(self, message):
        if self.os == 'Windows':
            ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, 2)
        elif self.os == 'Linux':
            # Check if X11 or something else
            if sys_os.environ.get('DISPLAY'):
                command = 'xset dpms force off'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    def CallbackTurnAllOn(self, message):
        if self.os == 'Windows':
            ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, -1)
        elif self.os == 'Linux':
            # Check if X11 or something else
            if sys_os.environ.get('DISPLAY'):
                command = 'xset dpms force on'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)
