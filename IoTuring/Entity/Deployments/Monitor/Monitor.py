import subprocess
import ctypes
import os
import re

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Entity import consts
from IoTuring.Logger.consts import STATE_OFF, STATE_ON


KEY_STATE = 'monitor_state'
KEY_CMD = 'monitor'


class Monitor(Entity):
    NAME = "Monitor"
    DEPENDENCIES = ["Os"]

    def Initialize(self):
        pass

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")
        
        supports_linux = False
        if self.os == consts.OS_FIXED_VALUE_LINUX:
            # Check if xset is working:
            p = subprocess.run(
                ['xset', 'dpms'], capture_output=True, shell=False)
            if p.stderr:
                raise Exception(f"Xset dpms error: {p.stderr.decode()}")
            elif not os.getenv('DISPLAY'):
                raise Exception('No $DISPLAY environment variable!')
            else:
                supports_linux = True

        if self.os == consts.OS_FIXED_VALUE_WINDOWS:
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.Callback))
        elif supports_linux:
            # Support for sending state on linux
            self.RegisterEntitySensor(EntitySensor(self, KEY_STATE))
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.Callback, KEY_STATE))

    def Callback(self, message):
        payloadString = message.payload.decode('utf-8')

        if payloadString == STATE_ON:
            if self.os == consts.OS_FIXED_VALUE_WINDOWS:
                ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, -1)
            elif self.os == consts.OS_FIXED_VALUE_LINUX:
                command = 'xset dpms force on'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)

        elif payloadString == STATE_OFF:
            if self.os == consts.OS_FIXED_VALUE_WINDOWS:
                ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, 2)
            elif self.os == consts.OS_FIXED_VALUE_LINUX:
                command = 'xset dpms force off'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        else:
            raise Exception('Incorrect payload!')

    def Update(self):
        if self.os == consts.OS_FIXED_VALUE_LINUX:
            p = subprocess.run(['xset', 'q'], capture_output=True, shell=False)
            outputString = p.stdout.decode()
            monitorState = re.findall(
                'Monitor is (.{2,3})', outputString)[0].upper()
            if monitorState in [STATE_OFF, STATE_ON]:
                self.SetEntitySensorValue(KEY_STATE, monitorState)
            else:
                raise Exception(f'Incorrect monitor state: {monitorState}')
