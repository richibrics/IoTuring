import os
from Entities.Entity import Entity


TOPIC = 'desktop_environment'

CONTENTS_VALUE_OPTION_KEY = "value"

class DesktopEnvironment(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def PostInitialize(self):
        # The value for this sensor is static for the entire script run time
        self.value=self.GetDesktopEnvironment()

    # I have also contents with value (optional) in config
    def EntitySchema(self):
        schema = super().EntitySchema()
        schema = schema.extend({
            self.schemas.Optional(self.consts.CONTENTS_OPTION_KEY):  {
                self.schemas.Optional(CONTENTS_VALUE_OPTION_KEY): str
            }
        })
        return schema

    def Update(self):
        self.SetTopicValue(TOPIC, self.value)

    # If value passed use it else get it from the system
    def GetDesktopEnvironment(self):

        de = os.environ.get('DESKTOP_SESSION')
        if de == None:
            de = "base"
       
        # If I have the value in the options, send that. otherwise try to get that                    
        return self.GetOption([self.consts.CONTENTS_OPTION_KEY,CONTENTS_VALUE_OPTION_KEY],de)
