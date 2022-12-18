from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.App import App
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity import consts

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

CONFIG_KEY_TITLE = "title"
CONFIG_KEY_MESSAGE = "message"

DEFAULT_DURATION = 10  # Seconds

MODE_DATA_VIA_CONFIG = "data_via_config"
MODE_DATA_VIA_PAYLOAD = "data_via_payload"

class Notify(Entity):
    NAME = "Notify"
    DEPENDENCIES = ["Os"]
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        try:
            self.config_title = self.GetConfigurations()[CONFIG_KEY_TITLE]
            self.config_message = self.GetConfigurations()[CONFIG_KEY_MESSAGE]
            self.data_mode = MODE_DATA_VIA_CONFIG
        except Exception as e:
            self.data_mode = MODE_DATA_VIA_PAYLOAD

        if self.data_mode == MODE_DATA_VIA_CONFIG:
            if not self.config_title or not self.config_message:
                self.data_mode = MODE_DATA_VIA_PAYLOAD

        if self.data_mode == MODE_DATA_VIA_CONFIG:
            self.Log(self.LOG_INFO, "Using data from configuration")
        else:
            self.Log(self.LOG_INFO, "Using data from payload")
            
        # In addition, if data is from payload, we add this info to entity name
        self.NAME = self.NAME + " (payload)" if self.data_mode == MODE_DATA_VIA_PAYLOAD else self.NAME

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
        preset.AddEntry("Notification title - leave empty to send this data via remote message", CONFIG_KEY_TITLE, mandatory=False)
        # ask for the message only if the title is provided, otherwise don't ask (use display_if_value_for_following_key_provided)
        preset.AddEntry("Notification message", CONFIG_KEY_MESSAGE, display_if_value_for_following_key_provided=CONFIG_KEY_TITLE, mandatory=True)
        return preset
