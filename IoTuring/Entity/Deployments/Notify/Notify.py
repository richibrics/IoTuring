from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand
from IoTuring.MyApp.App import App
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

import os
import json
import subprocess

supports_win = True
try:
    import tinyWinToast.tinyWinToast as twt  # type: ignore
except:
    supports_win = False

commands = {
    OsD.OS_FIXED_VALUE_LINUX: 'notify-send "{}" "{}" --icon="ICON_PATH"',
    OsD.OS_FIXED_VALUE_MACOS: 'osascript -e \'display notification "{}" with title "{}"\''
}


KEY = 'notify'

# To send notification data through message payload use these two
PAYLOAD_KEY_TITLE = "title"
PAYLOAD_KEY_MESSAGE = "message"
PAYLOAD_SEPARATOR = "|"

CONFIG_KEY_TITLE = "title"
CONFIG_KEY_MESSAGE = "message"
CONFIG_KEY_ICON_PATH = "icon_path"

DEFAULT_ICON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "icon.png")

MODE_DATA_VIA_CONFIG = "data_via_config"
MODE_DATA_VIA_PAYLOAD = "data_via_payload"


class Notify(Entity):
    NAME = "Notify"
    ALLOW_MULTI_INSTANCE = True

    # Data is set from configurations if configurations contain both title and message
    # Otherwise, data is set from payload (even if only one of title or message is set)
    def Initialize(self):

        # Check if both config is defined or both is empty:
        if not bool(self.GetConfigurations()[CONFIG_KEY_TITLE]) == bool(self.GetConfigurations()[CONFIG_KEY_MESSAGE]):
            raise Exception(
                "Configuration error: Both title and message should be defined, or both should be empty!")

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

        # Set and check icon path:
        self.config_icon_path = self.GetConfigurations()[CONFIG_KEY_ICON_PATH]

        if not os.path.exists(self.config_icon_path):
            self.Log(
                self.LOG_WARNING, f"Using default icon, custom path not found: {self.config_icon_path}")
            self.config_icon_path = DEFAULT_ICON_PATH

        # In addition, if data is from payload, we add this info to entity name
        # ! Changing the name we recognize the difference in warehouses only using the name
        # e.g HomeAssistant warehouse can use the regex syntax with NotifyPaylaod to identify that the component needs the text message
        self.NAME = self.NAME + \
            ("Payload" if self.data_mode == MODE_DATA_VIA_PAYLOAD else "")

        # Prepare the notification system
        if OsD.IsWindows():
            if not supports_win:
                raise Exception(
                    'Notify not available, have you installed \'tinyWinToast\' on pip ?')

        elif OsD.GetOs() in commands:
            if not OsD.CommandExists(commands[OsD.GetOs()].split(" ")[0]):
                raise Exception(
                    f'Command not found {commands[OsD.GetOs()].split(" ")[0]}!'
                )

            # Add icon to command:
            if "ICON_PATH" in commands[OsD.GetOs()]:
                self.command = commands[OsD.GetOs()].replace(
                    "ICON_PATH", self.config_icon_path)
            else:
                self.command = commands[OsD.GetOs()]

        else:
            raise Exception(
                'Notify not available for this platorm!')

        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback))

    def Callback(self, message):
        if self.data_mode == MODE_DATA_VIA_PAYLOAD:
            # Get data from payload:
            payloadString = message.payload.decode('utf-8')
            try:
                payloadMessage = json.loads(payloadString)
                self.notification_title = payloadMessage[PAYLOAD_KEY_TITLE]
                self.notification_message = payloadMessage[PAYLOAD_KEY_MESSAGE]
            except json.JSONDecodeError:
                payloadMessage = payloadString.split(PAYLOAD_SEPARATOR)
                self.notification_title = payloadMessage[0]
                self.notification_message = PAYLOAD_SEPARATOR.join(
                    payloadMessage[1:])
        else:  # self.data_mode = MODE_DATA_VIA_CONFIG
            self.notification_title = self.config_title
            self.notification_message = self.config_message

        # Check only the os (if it's that os, it's supported because if it wasn't supported,
        # an exception would be thrown in post-inits)
        if OsD.IsWindows():
            twt.getToast(
                title=self.notification_title,
                message=self.notification_message,
                icon=self.config_icon_path,
                appId=App.getName(),
                isMute=False).show()

        else:

            command = self.command.format(
                self.notification_title, self.notification_message)
            try:
                p = subprocess.run(command, capture_output=True, shell=True)
                self.Log(self.LOG_DEBUG, f"Called notify command: {p}")

                if p.stderr:
                    self.Log(self.LOG_ERROR,
                             f"Error during notify: {p.stderr.decode()}")

            except Exception as e:
                raise Exception('Error during notify: ' + str(e))


    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        preset.AddEntry("Notification title - leave empty to send this data via remote message",
                        CONFIG_KEY_TITLE, mandatory=False)
        # ask for the message only if the title is provided, otherwise don't ask (use display_if_key_value)
        preset.AddEntry("Notification message", CONFIG_KEY_MESSAGE,
                        display_if_key_value={CONFIG_KEY_TITLE: True}, mandatory=True)
        # Icon for notification, mac is not supported :(
        preset.AddEntry("Path to icon", CONFIG_KEY_ICON_PATH,
                        mandatory=False, default=DEFAULT_ICON_PATH)
        return preset
