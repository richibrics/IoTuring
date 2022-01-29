import os
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor 

KEY_DE = 'desktop_environment'

CONTENTS_VALUE_OPTION_KEY = "value"

# TODO Here I need the possibility for fixed value -> a configuration
class DesktopEnvironment(Entity):
    NAME = "DesktopEnvironment"
    
    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self,KEY_DE))

    def PostInitialize(self):
        # The value for this sensor is static for the entire script run time
        self.SetEntitySensorValue(KEY_DE,self.GetDesktopEnvironment())

    # If value passed use it else get it from the system
    def GetDesktopEnvironment(self):

        de = os.environ.get('DESKTOP_SESSION')
        if de == None:
            de = "base"
       
        return de
