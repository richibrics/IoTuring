import subprocess
import os as sys_os
from Entity.Entity import Entity 

TOPIC = 'sleep_command'

commands = {
    'Windows': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
    'Linux_X11': 'xset dpms force standby'
}


class Sleep(Entity):
    def Initialize(self):
        self.SubscribeToTopic(TOPIC)

    def PostInitialize(self):
        self.os=self.GetOS()

    def Callback(self, message):
        try:
            prefix = ''

            # Additional linux checking to find Window Manager
            # TODO: Update TurnOffMonitors, TurnOnMonitors, ShutdownCommand, LockCommand to use prefix lookup below
            if self.os == 'Linux':
                # Check running X11
                if sys_os.environ.get('DISPLAY'):
                    prefix = '_X11'

            lookup_key = self.os + prefix
            command = commands[lookup_key]
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)

        except:
            raise Exception(
                'No Sleep command for this Operating System')

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
