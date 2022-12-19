from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.App import App
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity import consts

import os

supports_win = True
try:
    import tinyWinToast.tinyWinToast as twt
except:
    supports_win = False


supports_unix = True
try:
    import notify2
except:
    supports_unix = False

KEY = 'notify'

CONFIG_KEY_TITLE = "title"
CONFIG_KEY_MESSAGE = "message"

DEFAULT_DURATION = 10  # Seconds

ICON_FILENAME = "icon.png"


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

        # Check if they have some value:
        if not (self.config_title and self.config_message):
            raise Exception("Configuration error: Title or message empty!")

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

    def PrepareMessage(self, message):
        self.notification_title = self.config_title
        self.notification_message = self.config_message

    def Callback(self, message):

        self.PrepareMessage(message)

        # Check only the os (if it's that os, it's supported because if it wasn't supported,
        # an exception would be thrown in post-inits)
        if self.os == consts.OS_FIXED_VALUE_WINDOWS:
            if DEFAULT_DURATION > 10:
                toast_duration = "long"
            else:
                toast_duration = "short"
            toast_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ICON_FILENAME)
            twt.getToast(
                title=self.notification_title, 
                message=self.notification_message,
                icon=toast_icon_path,
                duration=toast_duration,
                appId='IoTuring',
                isMute=False).show()

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
        preset.AddEntry("Notification title", CONFIG_KEY_TITLE, mandatory=True)
        preset.AddEntry("Notification message", CONFIG_KEY_MESSAGE, mandatory=True)
        return preset
