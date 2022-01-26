import subprocess
from Entity.Entity import Entity
from Entity.EntityData import EntityCommand

KEY_LOCK = 'lock'

commands = {
    'Windows': {
        'base': 'rundll32.exe user32.dll,LockWorkStation'
    },
    'macOS': {
        'base': 'pmset displaysleepnow'
    },
    'Linux': {
        'gnome': 'gnome-screensaver-command -l',
        'cinnamon': 'cinnamon-screensaver-command -a',
        'i3': 'i3lock'
    }
}


class Lock(Entity):
    NAME = "Lock"
    DEPENDENCIES = ["Os","DesktopEnvironment"]

    def Initialize(self):
        self.RegisterEntityCommand(EntityCommand(self,KEY_LOCK,self.Callback_Lock))

    def PostInitialize(self):
        pass

    def Callback_Lock(self, message):
        self.os = self.GetOS()
        self.de = self.GetDE()
        if self.os in commands:
            if self.de in commands[self.os]:
                try:
                    command = commands[self.os][self.de]
                    process = subprocess.Popen(
                        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:
                    raise Exception('Error during system lock: ' + str(e))
            else:
                raise Exception(
                    'No lock command for this Desktop Environment: ' + self.de)
        else:
            raise Exception(
                'No lock command for this Operating System: ' + self.os)

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()

    def GetDE(self):
        # Get OS from OsSensor and get temperature based on the os
        de = self.FindEntity(
            'DesktopEnvironment')
        if de:
            if not de.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                de.CallPostInitialize()
            de.CallUpdate()
            return de.GetTopicValue()
