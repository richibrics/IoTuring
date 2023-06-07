from IoTuring.Entity.Entity import Entity
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
import subprocess
import re

KEY = "terminal"
KEY_STATE = "terminal_state"

# possible values: payload command, sensor, binary sensor, button, switch, cover
CONFIG_KEY_ENTITY_TYPE = "entity_type"

# For payload commands:
CONFIG_KEY_COMMAND_REGEX = "command_regex"
CONFIG_KEY_LENGTH = "command_length"  # For payload validation

# For sensors only:
CONFIG_KEY_UNIT = "unit"
CONFIG_KEY_DECIMALS = "decimals"

# commands:
CONFIG_KEY_COMMAND_ON = "command_on"  # for payload, button, switch
CONFIG_KEY_COMMAND_OFF = "command_off"  # for switch
# for sensor, binary sensor, switch, cover
CONFIG_KEY_COMMAND_STATE = "command_state"

# cover commands
CONFIG_KEY_COMMAND_OPEN = "command_open"
CONFIG_KEY_COMMAND_CLOSE = "command_close"
CONFIG_KEY_COMMAND_STOP = "command_stop"

ENTITY_TYPE_KEYS = {
    "PAYLOAD_COMMAND": "payload_command",
    "BUTTON": "button",
    "SWITCH": "switch",
    "SENSOR": "sensor",
    "BINARY_SENSOR": "binary_sensor",
    "COVER": "cover"
}

COVER_STATES = {
    "opening": "OPEN",
    "closing": "CLOSE",
    "stopped": "STOP"
}


class Terminal(Entity):
    NAME = "Terminal"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):

        self.config_entity_type = self.GetConfigurations()[
            CONFIG_KEY_ENTITY_TYPE]

        # sanitize entity type:
        self.entity_type = str(
            self.config_entity_type).lower().strip().replace(" ", "_")

        if not self.entity_type in ENTITY_TYPE_KEYS.values():
            raise Exception(
                f"Configuration error: Unsupported entity type: {self.config_entity_type}")

        # Update the NAME
        name_extension = "".join([p.capitalize()
                                 for p in self.entity_type.split("_")])
        self.NAME += name_extension

        self.has_state = False
        self.has_binary_state = False
        self.has_command = False
        self.value_formatter_options = None
        self.custom_payload = {}

        # payload_command
        if self.entity_type == ENTITY_TYPE_KEYS["PAYLOAD_COMMAND"]:
            self.config_command_regex = \
                self.GetConfigurations()[CONFIG_KEY_COMMAND_REGEX]
            # Check if it's a correct regex:
            if not re.search(r"^\^.*\$$", self.config_command_regex):
                raise Exception(
                    f"Configuration error: Invalid regex: {self.config_command_regex}")

            # Get max length, use float so "inf" works
            self.config_length = float(
                self.GetConfigurations()[CONFIG_KEY_LENGTH])

            self.has_command = True

        # button
        elif self.entity_type == ENTITY_TYPE_KEYS["BUTTON"]:
            self.config_command = self.GetConfigurations()[
                CONFIG_KEY_COMMAND_ON]
            self.has_command = True

        # switch
        elif self.entity_type == ENTITY_TYPE_KEYS["SWITCH"]:
            self.config_command_on = \
                self.GetConfigurations()[CONFIG_KEY_COMMAND_ON]
            self.config_command_off = \
                self.GetConfigurations()[CONFIG_KEY_COMMAND_OFF]
            self.has_command = True

            if self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]:
                self.config_command_state = \
                    self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]
                self.has_binary_state = True

        # sensor
        elif self.entity_type == ENTITY_TYPE_KEYS["SENSOR"]:
            self.config_command_state = \
                self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]
            self.has_state = True

            self.config_unit = self.GetConfigurations()[CONFIG_KEY_UNIT]
            if self.config_unit:
                self.custom_payload["unit_of_measurement"] = self.config_unit

            if self.GetConfigurations()[CONFIG_KEY_DECIMALS]:
                self.value_formatter_options = \
                    ValueFormatterOptions(value_type=ValueFormatterOptions.TYPE_NONE,
                                          decimals=int(self.GetConfigurations()[CONFIG_KEY_DECIMALS]))

        # binary sensor
        elif self.entity_type == ENTITY_TYPE_KEYS["BINARY_SENSOR"]:
            self.config_command_state = \
                self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]
            self.has_binary_state = True

        # cover
        elif self.entity_type == ENTITY_TYPE_KEYS["COVER"]:
            self.config_cover_commands = {
                "OPEN": self.GetConfigurations()[CONFIG_KEY_COMMAND_OPEN],
                "CLOSE": self.GetConfigurations()[CONFIG_KEY_COMMAND_CLOSE]
            }

            stop_command = self.GetConfigurations()[CONFIG_KEY_COMMAND_STOP]

            if stop_command:
                self.config_cover_commands["STOP"] = stop_command
            else:
                self.custom_payload["payload_stop"] = None

            self.has_command = True

            self.config_command_state = \
                self.GetConfigurations()[CONFIG_KEY_COMMAND_STATE]

            if self.config_command_state:
                self.has_state = True
            else:
                self.custom_payload["optimistic"] = "true"

        else:
            raise Exception("Configuration error: Unknown entity type")

        # The sensor is for displaying extra attributes for commands:
        self.RegisterEntitySensor(
            EntitySensor(self, KEY_STATE,
                         supportsExtraAttributes=True,
                         valueFormatterOptions=self.value_formatter_options,
                         customPayload=self.custom_payload))

        if self.has_command:
            self.RegisterEntityCommand(EntityCommand(
                self, KEY, self.Callback, KEY_STATE))

        # Defaults for attributes:
        self.last_command = ""
        self.last_output = ""
        self.state = ""
        self.state_message = ""

    def Callback(self, message):

        # Get data from payload:
        payloadString = message.payload.decode('utf-8')
        self.Log(self.LOG_DEBUG,
                 f"Decoded payload string: {payloadString}")

        if self.entity_type == ENTITY_TYPE_KEYS["PAYLOAD_COMMAND"]:
            # Check regex and max length
            if re.search(self.config_command_regex, payloadString) \
                    and not len(payloadString) > self.config_length:
                self.command = payloadString
            else:
                raise Exception(f"Invalid payload: {payloadString}")

        elif self.entity_type == ENTITY_TYPE_KEYS["BUTTON"]:
            self.command = self.config_command

        elif self.entity_type == ENTITY_TYPE_KEYS["SWITCH"]:
            if payloadString == STATE_ON:
                self.command = self.config_command_on
            elif payloadString == STATE_OFF:
                self.command = self.config_command_off
            else:
                raise Exception(f"Invalid payload: {payloadString}")

        elif self.entity_type == ENTITY_TYPE_KEYS["COVER"]:
            cover_command = payloadString.upper()
            if not cover_command in self.config_cover_commands.keys():
                raise Exception(f"Invalid payload: {payloadString}")

            self.command = self.config_cover_commands[cover_command]

            if not self.command:
                raise Exception(f"No command for payload: {payloadString}")

        self.last_command = self.command

        # Run the command, collect output for update:
        command = self.RunCommand(self.command)
        self.last_output = command["message"]

    def Update(self):

        if self.has_binary_state or self.has_state:

            # Run the command, do not log error on binary sensor:
            command = self.RunCommand(self.config_command_state,
                                      log_errors=not self.has_binary_state)

            if self.has_binary_state:
                self.state = STATE_ON if command["returncode"] == 0 else STATE_OFF

            elif self.has_state:

                if self.entity_type == ENTITY_TYPE_KEYS["COVER"]:
                    cmdout = command["stdout"].lower()
                    if cmdout in COVER_STATES.keys():
                        self.state = COVER_STATES[cmdout]
                    else:
                        self.Log(self.LOG_ERROR,
                                 f"Invalid state: {command['stdout']}")

                else:
                    self.state = command["stdout"]

                    # Parse state
                    try:
                        self.state = float(self.state)
                    except ValueError:
                        if self.value_formatter_options or self.config_unit:
                            self.Log(self.LOG_ERROR,
                                     f"Invalid state: {self.state}")

            self.SetEntitySensorValue(KEY_STATE, self.state)
            self.SetEntitySensorExtraAttribute(
                KEY_STATE, "Last state command output", command["message"])

        if self.has_command:
            # Set extra attributes:
            self.SetEntitySensorExtraAttribute(
                KEY_STATE, "Last command", self.last_command)
            self.SetEntitySensorExtraAttribute(
                KEY_STATE, "Last output", self.last_output)

    def RunCommand(self, command, log_errors=True):
        """Run a command, log, collect output"""

        # Run the command:
        p = subprocess.run(command, capture_output=True,
                           shell=True, universal_newlines=True)

        output = {
            "returncode": p.returncode,
            "stdout": p.stdout,
            "message": ""
        }

        # Log output and error:
        if p.stderr:
            output["message"] = "Error: " + p.stderr
            loglevel = self.LOG_ERROR if log_errors else self.LOG_DEBUG
            self.Log(loglevel,
                     f"Error running command '{command}': {p.stderr}")
        else:
            output["message"] = p.stdout
            self.Log(self.LOG_DEBUG,
                     f"Command '{command}' run, stdout: {p.stdout}")
        return output

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()
        preset.AddEntry("Entity type (payload command, sensor, binary sensor, button, switch or cover)",
                        CONFIG_KEY_ENTITY_TYPE, mandatory=True, modify_value_callback=MenuPreset.Callback_LowerAndStripString)

        # payload command
        preset.AddEntry("Regex for filter the incoming payload: Use ^ as the first and $ as the last character",
                        CONFIG_KEY_COMMAND_REGEX, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "payload command"})
        preset.AddEntry("Maximum command length", CONFIG_KEY_LENGTH, mandatory=False, default="inf",
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "payload command"})

        # button
        preset.AddEntry("Terminal command to run",
                        CONFIG_KEY_COMMAND_ON, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "button"})

        # switch
        preset.AddEntry("Terminal command to switch ON",
                        CONFIG_KEY_COMMAND_ON, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "switch"})
        preset.AddEntry("Terminal command to switch OFF",
                        CONFIG_KEY_COMMAND_OFF, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "switch"})
        preset.AddEntry("Terminal command for STATE of the switch, leave empty for an optimistic switch. The command must return 0 for ON state",
                        CONFIG_KEY_COMMAND_STATE, mandatory=False,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "switch"})

        # sensor
        preset.AddEntry("Terminal command to get the sensor value",
                        CONFIG_KEY_COMMAND_STATE, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "sensor"})
        preset.AddEntry("Unit of measurement",
                        CONFIG_KEY_UNIT, mandatory=False,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "sensor"})
        preset.AddEntry("Number of decimals",
                        CONFIG_KEY_DECIMALS, mandatory=False,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "sensor"})

        # binary sensor
        preset.AddEntry("Terminal command, exit code must be 0 for ON state",
                        CONFIG_KEY_COMMAND_STATE, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "binary sensor"})

        # cover
        preset.AddEntry("Terminal command to OPEN",
                        CONFIG_KEY_COMMAND_OPEN, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "cover"})
        preset.AddEntry("Terminal command to CLOSE",
                        CONFIG_KEY_COMMAND_CLOSE, mandatory=True,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "cover"})
        preset.AddEntry("Terminal command to STOP",
                        CONFIG_KEY_COMMAND_STOP, mandatory=False,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "cover"})
        preset.AddEntry("Terminal command for STATE, leave empty for optimistic. Command must return 'opening', 'closing' or 'stopped'",
                        CONFIG_KEY_COMMAND_STATE, mandatory=False,
                        display_if_key_value={CONFIG_KEY_ENTITY_TYPE: "cover"})
        return preset
