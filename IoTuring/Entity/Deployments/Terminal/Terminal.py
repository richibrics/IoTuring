from IoTuring.Entity.Entity import Entity
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON
import subprocess
import re

KEY = "terminal"
KEY_STATE = "terminal_state"

CONFIG_KEY_COMMAND_ON = "command_on"
CONFIG_KEY_LENGTH = "length"
CONFIG_KEY_COMMAND_OFF = "command_off"
CONFIG_KEY_COMMAND_STATE = "command_state"


MODE_DATA_VIA_CONFIG = "data_via_config"
MODE_DATA_VIA_PAYLOAD = "data_via_payload"
MODE_SWITCH_WITH_STATE = "switch_with_state"
MODE_SWITCH_WITHOUT_STATE = "switch_without_state"


# If a string matches this, it's a regex:
REGEX_IS_REGEX = r"^\^.*\$$"


class Terminal(Entity):
    NAME = "Terminal"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):

        # Commands from config:
        self.config_command_on = \
            self.GetConfigurations()[CONFIG_KEY_COMMAND_ON]
        self.config_command_off = \
            self.GetConfigurations()[CONFIG_KEY_COMMAND_OFF]
        self.config_command_state = \
            self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]

        # Set max length to infinite:
        self.config_length = float('inf')
        self.switch_mode = False

        # It's regex based, exact command from payload:
        if re.search(REGEX_IS_REGEX, self.config_command_on):
            self.data_mode = MODE_DATA_VIA_PAYLOAD
            if self.GetConfigurations()[CONFIG_KEY_LENGTH]:
                self.config_length = int(
                    self.GetConfigurations()[CONFIG_KEY_LENGTH])

        # It's config based:
        else:
            self.data_mode = MODE_DATA_VIA_CONFIG
            if self.GetConfigurations()[CONFIG_KEY_LENGTH]:
                raise Exception(
                    "Configuration error: Command length should given only in regex mode")

            # It's a switch:
            if self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]:
                self.switch_mode = MODE_SWITCH_WITH_STATE
            elif self.GetConfigurations()[CONFIG_KEY_COMMAND_OFF]:
                self.switch_mode = MODE_SWITCH_WITHOUT_STATE
                self.optimistic = True

        # Update name based on mode:
        if self.data_mode == MODE_DATA_VIA_PAYLOAD:
            self.NAME += "Payload"
        elif self.switch_mode:
            self.NAME += "Switch"

        # Defaults for extra attributes:
        self.last_command = ""
        self.last_output = ""

        # The sensor is for displaying extra attributes:
        self.RegisterEntitySensor(
            EntitySensor(self, KEY_STATE, supportsExtraAttributes=True))
        self.RegisterEntityCommand(EntityCommand(
            self, KEY, self.Callback, KEY_STATE))

    def Callback(self, message):

        # Get data from payload:
        payloadString = message.payload.decode('utf-8')

        if self.data_mode == MODE_DATA_VIA_PAYLOAD:
            # Check regex and max length
            if re.search(self.config_command_on, payloadString) \
                    and not len(payloadString) > self.config_length:
                self.command = payloadString
            else:
                raise Exception(f"Invalid payload: {payloadString}")

        elif self.switch_mode:
            if payloadString == STATE_ON:
                self.command = self.config_command_on
            elif payloadString == STATE_OFF:
                self.command = self.config_command_off
            else:
                raise Exception('Incorrect payload!')

        else:  # self.data_mode = MODE_DATA_VIA_CONFIG
            self.command = self.config_command_on

        self.last_command = self.command

        # Run the command, collect output for update:
        command = self.RunCommand(self.command)
        self.last_output = command["message"]

    def Update(self):
        if self.switch_mode == MODE_SWITCH_WITH_STATE:
            # Run the command:
            command = self.RunCommand(self.config_command_state, False)

            state = STATE_ON if command["returncode"] == 0 else STATE_OFF

            self.SetEntitySensorValue(KEY_STATE, state)
            self.SetEntitySensorExtraAttribute(
                KEY_STATE, "Last state command output", command["message"])

        # Set extra attributes:
        self.SetEntitySensorExtraAttribute(
            KEY_STATE, "Last command", self.last_command)
        self.SetEntitySensorExtraAttribute(
            KEY_STATE, "Last output", self.last_output)

    def RunCommand(self, command, log_errors=True):
        """Run a command, log, collect output"""

        # Run the command:
        p = subprocess.run(command, capture_output=True, shell=True)

        output = {
            "returncode": p.returncode,
            "message": ""
        }

        # Log output and error:
        if p.stderr:
            output["message"] = "Error: " + p.stderr.decode()
            loglevel = self.LOG_ERROR if log_errors else self.LOG_DEBUG
            self.Log(loglevel,
                     f"Error running command '{command}': {p.stderr.decode()}")
        else:
            output["message"] = p.stdout.decode()
            self.Log(self.LOG_DEBUG,
                     f"Command '{command}' run, stdout: {p.stdout.decode()}")
        return output

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()
        preset.AddEntry("Terminal command or regex - For regex use ^ as the first and $ as the last character",
                        CONFIG_KEY_COMMAND_ON, mandatory=True)
        preset.AddEntry("Maximum command length", CONFIG_KEY_LENGTH,
                        display_if_key_value_regex_match={CONFIG_KEY_COMMAND_ON: REGEX_IS_REGEX}, mandatory=False)
        # The regex here matches, if the first command was not a regex:
        preset.AddEntry("OFF command for creating a switch, leave empty to use only a the previous command",
                        CONFIG_KEY_COMMAND_OFF, mandatory=False,
                        display_if_key_value_regex_match={CONFIG_KEY_COMMAND_ON: r"^[^^]|.*[^\$]$"})
        preset.AddEntry("Terminal command for STATE of the switch, leave empty for an optimistic switch. The command must return 0 for ON state",
                        CONFIG_KEY_COMMAND_STATE, mandatory=False,
                        display_if_key_value_regex_match={CONFIG_KEY_COMMAND_OFF: True})

        return preset
