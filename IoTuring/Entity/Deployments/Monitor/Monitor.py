import subprocess
import ctypes
import os as sys_os
from IoTuring.Entity.Entity import Entity
from ctypes import *

from IoTuring.Entity.EntityData import EntityCommand

KEY_TURN_ALL_OFF = 'turn_all_off'
KEY_TURN_ALL_ON = 'turn_all_on'
KEY_INTERNAL_MONITOR = "internal"
KEY_EXTERNAL_MONITOR = "external"
KEY_EXTEND_MONITOR = "extend"
KEY_CLONE_MONITOR = "clone"


class Monitor(Entity):
    NAME = "Monitor"
    DEPENDENCIES = ["Os"]

    def Initialize(self):
        pass

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")

        if self.os == 'Windows' or (self.os == 'Linux' and sys_os.environ.get('DISPLAY')):
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_TURN_ALL_OFF, self.CallbackTurnAllOff))
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_TURN_ALL_ON, self.CallbackTurnAllOn))
            sr = sys_os.environ.get('SystemRoot')
            if self.os == 'Windows' and sys_os.path.exists('{}\System32\DisplaySwitch.exe'.format(sr)):
                self.RegisterEntityCommand(EntityCommand(
                    self, KEY_INTERNAL_MONITOR, self.CallbackInternalMonitor))
                self.RegisterEntityCommand(EntityCommand(
                    self, KEY_EXTERNAL_MONITOR, self.CallbackExternalMonitor))
                self.RegisterEntityCommand(EntityCommand(
                    self, KEY_EXTEND_MONITOR, self.CallbackExtendMonitor))
                self.RegisterEntityCommand(EntityCommand(
                    self, KEY_CLONE_MONITOR, self.CallbackCloneMonitor))

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

    def CallbackInternalMonitor(self, message):
        if self.os == 'Windows':
            sr = sys_os.environ.get('SystemRoot')
            command = '{}\System32\DisplaySwitch.exe /internal'.format(sr)
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    def CallbackExternalMonitor(self, message):
        if self.os == 'Windows':
            sr = sys_os.environ.get('SystemRoot')
            command = '{}\System32\DisplaySwitch.exe /external'.format(sr)
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    def CallbackExtendMonitor(self, message):
        if self.os == 'Windows':
            sr = sys_os.environ.get('SystemRoot')
            command = '{}\System32\DisplaySwitch.exe /extend'.format(sr)
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    def CallbackCloneMonitor(self, message):
        if self.os == 'Windows':
            sr = sys_os.environ.get('SystemRoot')
            command = '{}\System32\DisplaySwitch.exe /clone'.format(sr)
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)
