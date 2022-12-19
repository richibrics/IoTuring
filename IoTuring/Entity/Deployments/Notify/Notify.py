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

commands = {
    consts.OS_FIXED_VALUE_LINUX: 'notify-send "{}" "{}"',
    consts.OS_FIXED_VALUE_MACOS: 'osascript -e \'display notification "{}" with title "{}"\''
}


KEY = 'notify'

CONFIG_KEY_TITLE = "title"
CONFIG_KEY_MESSAGE = "message"

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
                    'Notify not available, have you installed \'tinyWinToast\' on pip ?')

        elif self.os == consts.OS_FIXED_VALUE_LINUX \
            or self.os == consts.OS_FIXED_VALUE_MACOS:
            # Use 'command -v' to test if comman exists:
            if os.system(f'command -v {commands[self.os].split(" ")[0]}') != 0:
                raise Exception(
                    f'Command not found {commands[self.os].split(" ")[0]}!'
                )
                
        else:
            raise Exception(
                'Notify not available for this platorm!')

    def PrepareMessage(self, message):
        self.notification_title = self.config_title
        self.notification_message = self.config_message

    def Callback(self, message):

        self.PrepareMessage(message)

        # Check only the os (if it's that os, it's supported because if it wasn't supported,
        # an exception would be thrown in post-inits)
        if self.os == consts.OS_FIXED_VALUE_WINDOWS:
            toast_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ICON_FILENAME)
            twt.getToast(
                title=self.notification_title, 
                message=self.notification_message,
                icon=toast_icon_path,
                appId=App.getName(),
                isMute=False).show()

        elif self.os == consts.OS_FIXED_VALUE_LINUX:
            os.system(commands[self.os]
                .format(self.notification_title,self.notification_message))

        elif self.os == consts.OS_FIXED_VALUE_MACOS:
            os.system(commands[self.os]
                .format(self.notification_message,self.notification_title))

        else:
            self.Log(self.LOG_WARNING, "No notify command available for this operating system (" +
                     str(self.os) + ")... Aborting")

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Notification title", CONFIG_KEY_TITLE, mandatory=True)
        preset.AddEntry("Notification message", CONFIG_KEY_MESSAGE, mandatory=True)
        return preset
