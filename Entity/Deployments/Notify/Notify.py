from Entity.Entity import Entity
from Entity.EntityData import EntityCommand 
from MyApp.App import App

from Configurator.MenuPreset import MenuPreset

import os

from Entity import consts

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

class Notify(Entity):
    NAME = "Notify"
    DEPENDENCIES = ["Os"]
    ALLOW_MULTI_INSTANCE = True
    
    def Initialize(self):
        try:
            self.notification_title = self.GetConfigurations()[CONFIG_KEY_TITLE]
            self.notification_message = self.GetConfigurations()[CONFIG_KEY_MESSAGE]
        except Exception as e:
            raise Exception("Configuration error: " + str(e))

        self.RegisterEntityCommand(EntityCommand(self,KEY,self.Callback))

    # I need it here cause I have to check the right import for my OS (and I may not know the OS in Init function)
    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue("Os","operating_system")
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
        # TO DO
        # Convert the payload in a dict
        messageDict = ''
        try:
            messageDict = eval(message.payload.decode('utf-8'))
        except:
            pass  # No message or title in the payload

        # Priority for configuration content and title. If not set there, will try to find them in the payload

        # Check only the os (if it's that os, it's supported because if it wasn't supported,
        # an exception would be thrown in post-inits)
        if self.os == consts.OS_FIXED_VALUE_WINDOWS:
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(
                self.notification_title, self.notification_message, duration=DEFAULT_DURATION, threaded=False)
        elif self.os == consts.OS_FIXED_VALUE_LINUX:
            notification = notify2.Notification(self.notification_title, self.notification_message)
            notification.show()
        elif self.os == consts.OS_FIXED_VALUE_MACOS:
            command = 'osascript -e \'display notification "{}" with title "{}"\''.format(
                self.notification_message, self.notification_title,)
            os.system(command)
        else:
            self.Log(self.Logger.LOG_WARNING,"No notify command available for this operating system ("+ str(self.os) +")... Aborting")

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Notification title", CONFIG_KEY_TITLE, mandatory=True)
        preset.AddEntry("Notification message", CONFIG_KEY_MESSAGE, mandatory=True)
        return preset
