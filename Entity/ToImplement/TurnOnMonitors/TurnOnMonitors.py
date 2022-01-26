import subprocess
import ctypes
import os as sys_os
from Entity.Entity import Entity 
from ctypes import *

TOPIC = 'turn_on_monitors_command'


class TurnOnMonitors(Entity):
    def Initialize(self):
        self.SubscribeToTopic(TOPIC)

    def PostInitialize(self):
        self.os = self.GetOS()

    def Callback(self, message):
        if self.os == 'Windows':
            ctypes.windll.user32.SendMessageA(0xFFFF, 0x0112, 0xF170, -1)  # Untested
        elif self.os == 'Linux':
            # Check if X11 or something else
            if sys_os.environ.get('DISPLAY'):
                command = 'xset dpms force on'
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            else:
                raise Exception(
                    'The Turn ON Monitors command is not available for this Linux Window System')

        else:
            raise Exception(
                'The Turn ON Monitors command is not available for this Operating System')

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
