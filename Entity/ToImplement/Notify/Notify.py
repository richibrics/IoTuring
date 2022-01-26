import os
from Entity.Entity import Entity 
from Logger import Logger, ExceptionTracker

supports_win = True
try:
    import win10toast
except:
    supports_win = False


supports_unix = True
try:
    import notify2  # Only to get windows temperature
except:
    supports_unix = False


TOPIC = 'notify'

# If I haven't value for the notification I use these
DEFAULT_MESSAGE = 'Notification'
DEFAULT_TITLE = 'PyMonitorMQTT'

DEFAULT_DURATION = 10  # Seconds

# SAME KEYS MUST BE PLACED IN THE PAYLOAD OF THE MESSAGE IF YOU WANT TO PASS FROM THERE
CONTENTS_TITLE_OPTION_KEY = "title"
CONTENTS_MESSAGE_OPTION_KEY = "message" 

class Notify(Entity):
    def Initialize(self):
        self.SubscribeToTopic(TOPIC)

    # I have also contents with title and message (optional) in config
    def EntitySchema(self):
        schema = super().EntitySchema()
        schema = schema.extend({
            self.schemas.Optional(self.consts.CONTENTS_OPTION_KEY):  {
                self.schemas.Optional(CONTENTS_TITLE_OPTION_KEY): str,
                self.schemas.Optional(CONTENTS_MESSAGE_OPTION_KEY): str
            }
        })
        return schema

    # I need it here cause I have to check the right import for my OS (and I may not know the OS in Init function)
    def PostInitialize(self):
        self.os = self.GetOS()
        if self.os == self.consts.FIXED_VALUE_OS_WINDOWS:
            if not supports_win:
                raise Exception(
                    'Notify not available, have you installed \'win10toast\' on pip ?')
        elif self.os == self.consts.FIXED_VALUE_OS_LINUX:
            if supports_unix:
                # Init notify2
                notify2.init('PyMonitorMQTT')
            else:
                raise Exception(
                    'Notify not available, have you installed \'notify2\' on pip ?')

    def Callback(self, message):
        # TO DO
        # Convert the payload in a dict
        messageDict = ''
        try:
            messageDict = eval(message.payload.decode('utf-8'))
        except:
            pass  # No message or title in the payload

        # Priority for configuration content and title. If not set there, will try to find them in the payload

        # Look for notification content
        if self.GetOption([self.consts.CONTENTS_OPTION_KEY,CONTENTS_MESSAGE_OPTION_KEY]): # In config ?
            content = self.GetOption([self.consts.CONTENTS_OPTION_KEY,CONTENTS_MESSAGE_OPTION_KEY])
        elif CONTENTS_MESSAGE_OPTION_KEY in messageDict: # In the payload ?
            content = messageDict[CONTENTS_MESSAGE_OPTION_KEY]
        else: # Nothing found: use default
            content = DEFAULT_MESSAGE
            self.Log(Logger.LOG_WARNING,
                     'No message for the notification set in configuration or in the received payload')

        # Look for notification title
        if self.GetOption([self.consts.CONTENTS_OPTION_KEY,CONTENTS_TITLE_OPTION_KEY]): # In config ?
            title = self.GetOption([self.consts.CONTENTS_OPTION_KEY,CONTENTS_TITLE_OPTION_KEY])
        elif CONTENTS_TITLE_OPTION_KEY in messageDict: # In the payload ?
            title = messageDict[CONTENTS_TITLE_OPTION_KEY]
        else: # Nothing found: use default
            title = DEFAULT_TITLE

        # Check only the os (if it's that os, it's supported because if it wasn't supported,
        # an exception would be thrown in post-inits)
        if self.os == self.consts.FIXED_VALUE_OS_WINDOWS:
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(
                title, content, duration=DEFAULT_DURATION, threaded=False)
        elif self.os == self.consts.FIXED_VALUE_OS_LINUX:
            notification = notify2.Notification(title, content)
            notification.show()
        elif self.os == self.consts.FIXED_VALUE_OS_MACOS:
            command = 'osascript -e \'display notification "{}" with title "{}"\''.format(
                content, title)
            os.system(command)
        else:
            self.Log(self.Logger.LOG_WARNING,"No notify command available for this operating system ("+ str(self.os) +")... Aborting")

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
