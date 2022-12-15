from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity import consts
from IoTuring.Entity.Deployments.Notify.Notify import Notify

import os

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

DEFAULT_DURATION = 10  # Seconds


class NotifyPayload(Notify):
    NAME = "NotifyPayload"
    DEPENDENCIES = ["Os"]
    ALLOW_MULTI_INSTANCE = False

    def Initialize(self):
        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback))

    def PrepareMessage(self, message):
        messageDict = ''
        try:
            messageDict = eval(message.payload.decode('utf-8'))
            self.notification_title = messageDict[PAYLOAD_KEY_TITLE]
            self.notification_message = messageDict[PAYLOAD_KEY_MESSAGE]
        except:
            raise Exception(
                'Incorrect payload and no title and message set in configuration!'
            )

    @classmethod
    def ConfigurationPreset(self):
        return None
