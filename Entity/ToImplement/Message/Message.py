import os
from Entity.Entity import Entity 


TOPIC = 'message'
default_message = "default"

config_content_message_key = "message"

class Message(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def PostInitialize(self): # for this topic the value is fixed in cofniguration so I don't need to get it from there at every update
        self.value=self.GetOption([self.consts.CONTENTS_OPTION_KEY,config_content_message_key],default_message)

    # I have also contents with message (required) in config
    def EntitySchema(self):
        schema = super().EntitySchema()
        schema = schema.extend({
            self.schemas.Required(self.consts.CONTENTS_OPTION_KEY):  {
                self.schemas.Required(config_content_message_key): str
            }
        })
        return schema

    def Update(self):
        self.SetTopicValue(TOPIC, self.value)
