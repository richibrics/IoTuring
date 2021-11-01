from Entities.Entity import Entity
from os import path
from ctypes import *

TOPIC_LEVEL = 'volume/level_get'
TOPIC_MUTE = 'volume/mute_get'

scriptFolder = str(path.dirname(path.realpath(__file__)))
#EXTERNAL_SOFTWARE_FILENAME = path.join(scriptFolder,'..','..','ExternalUtilities','FILE')


class Volume(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC_LEVEL)
        self.AddTopic(TOPIC_MUTE)

    def PostInitialize(self):
        os = self.GetOS()
        self.UpdateSpecificFunction = None   # Specific function for this os/de, set this here to avoid all if else except at each update
        
        raise Exception('No volume sensor available')

    def Update(self):
        self.SetTopicValue(TOPIC, self.UpdateSpecificFunction())

    def GetWindowsVolume(self):
        pass

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
