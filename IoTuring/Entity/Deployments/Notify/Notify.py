from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.App import App

from IoTuring.Configurator.MenuPreset import MenuPreset

import os

from IoTuring.Entity import consts

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

CONFIG_KEY_TITLE = "title"
CONFIG_KEY_MESSAGE = "message"

DEFAULT_DURATION = 10  # Seconds


class Notify(Entity):
    NAME = "Notify"
    DEPENDENCIES = ["Os"]
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        try:
            self.config_title = self.GetConfigurations()[CONFIG_KEY_TITLE]
            self.config_message = self.GetConfigurations()[CONFIG_KEY_MESSAGE]
        except Exception as e:
            raise Exception("Configuration error: " + str(e))

        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback))

    # I need it here cause I have to check the right import for my OS (and I may not know the OS in Init function)
    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue("Os", "operating_system")
        if self.os == consts.OS_FIXED_VALUE_WINDOWS:
            if not supports_win:
                raise Exception(
                    'Notify not available, have you installed \'win10toast\' on pip ?')
        elif self.os == consts.OS_FIXED_VALUE_LINUX:
            if supports_unix:
                # Init notify2
                notify2.init(App.getName())
            else:
                raise Exception(
                    'Notify not available, have you installed \'notify2\' on pip ?')

    def Callback(self, message):

        # Priority for configuration content and title. If not set there, will try to find them in the payload
        if self.config_title and self.config_message:
            self.notification_title = self.config_title
            self.notification_message = self.config_message

        else:
            # Convert the payload to a dict:
            messageDict = ''
            try:
                messageDict = eval(message.payload.decode('utf-8'))
                self.notification_title = messageDict[PAYLOAD_KEY_TITLE]
                self.notification_message = messageDict[PAYLOAD_KEY_MESSAGE]
            except:
                raise Exception(
                    'Incorrect payload and no title and message set in configuration!'
                )

        # Check only the os (if it's that os, it's supported because if it wasn't supported,
        # an exception would be thrown in post-inits)
        if self.os == consts.OS_FIXED_VALUE_WINDOWS:
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(
                self.notification_title, self.notification_message, duration=DEFAULT_DURATION, threaded=False)
        elif self.os == consts.OS_FIXED_VALUE_LINUX:
            notification = notify2.Notification(
                self.notification_title, self.notification_message)
            notification.show()
        elif self.os == consts.OS_FIXED_VALUE_MACOS:
            command = 'osascript -e \'display notification "{}" with title "{}"\''.format(
                self.notification_message, self.notification_title,)
            os.system(command)
        else:
            self.Log(self.LOG_WARNING, "No notify command available for this operating system (" +
                     str(self.os) + ")... Aborting")

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry(
            "Notification title (Leave empty if you want to define it in the payload)", CONFIG_KEY_TITLE)
        preset.AddEntry(
            "Notification message (Leave empty if you want to define it in the payload)", CONFIG_KEY_MESSAGE)
        return preset
