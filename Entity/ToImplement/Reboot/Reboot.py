import subprocess
from Entity.Entity import Entity 

TOPIC = 'reboot_command'

commands = {
    'Windows': 'shutdown /r',
    'macOS': 'sudo reboot',
    'Linux': 'sudo reboot'
}


class Reboot(Entity):
    def Initialize(self):
        self.SubscribeToTopic(TOPIC)

    def PostInitialize(self):
        self.os = self.GetOS()

    def Callback(self, message):
        try:
            command = commands[self.os]
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        except:
            raise Exception(
                'No reboot command for this Operating System')

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
