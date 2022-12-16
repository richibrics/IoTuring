from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity import consts
from IoTuring.Entity.Deployments.Notify.Notify import Notify

import os
import json

supports_win = True
try:
    import win10toast
except:
    supports_win = False


supports_unix = True
try:
    import notify2
except:
    supports_unix = False

KEY = 'notify'

# To send notification data through message payload use these two
PAYLOAD_KEY_TITLE = "title"
PAYLOAD_KEY_MESSAGE = "message"
PAYLOAD_SEPARATOR = "|"

DEFAULT_DURATION = 10  # Seconds


class NotifyPayload(Notify):
    NAME = "NotifyPayload"
    DEPENDENCIES = ["Os"]
    ALLOW_MULTI_INSTANCE = False

    def Initialize(self):
        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback))

    def PrepareMessage(self, message):
        payloadString = message.payload.decode('utf-8')

        try:    
            payloadMessage = json.loads(payloadString)
            self.notification_title = payloadMessage[PAYLOAD_KEY_TITLE]
            self.notification_message = payloadMessage[PAYLOAD_KEY_MESSAGE]            
        
        except json.JSONDecodeError:
            payloadMessage = payloadString.split(PAYLOAD_SEPARATOR)
            self.notification_title = payloadMessage[0]
            self.notification_message = PAYLOAD_SEPARATOR.join(payloadMessage[1:])
        
        except:
            raise Exception('Incorrect payload!')

    @classmethod
    def ConfigurationPreset(self):
        return None
