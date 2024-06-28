from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

from subprocess import check_output, STDOUT
KEY = "wlrctl"
KEY_STATE = "wlrctl_state"


CONFIG_KEY_DOMAIN = "domain"
DOMAIN_CHOICES = [
    {"name": "Keyboard", "value": "keyboard"},
    {"name": "Pointer", "value": "pointer"},
    {"name": "ToplevelCommand", "value": "toplevelcommand"},
    {"name": "ToplevelSensor", "value": "toplevelsensor"},
    {"name": "Output", "value": "output"},
]

#Keyboard Domain
CONFIG_KEY_KEYBOARD_ACTION = "keyboard_action"
KEYBOARD_ACTIONS = [
    {"name": "Type", "value": "type"},
]
KEYBOARD_ACTIONS_INSTRUCTIONS = """
    Type: types a given string into the focused client"
    """

CONFIG_KEY_KEYBOARD_KEYS = "keys"
CONFIG_KEY_KEYBOARD_MODIFIERS = "modifiers"
KEYBOARD_MODIFIERS = [
    {"name": "Shift", "value": "SHIFT"},
    {"name": "Ctrl", "value": "CTRL"},
    {"name": "Alt", "value": "ALT"},
    {"name": "Super", "value": "SUPER"},
]

# Pointer Domain
CONFIG_KEY_POINTER_ACTION = "pointer_action"
POINTER_ACTIONS = [
    {"name": "Click", "value": "click"},
    {"name": "Move", "value": "move"},
    {"name": "Scroll", "value": "scroll"},
]

POINTER_ACTIONS_INSTRUCTIONS = """
    Click:  clicks the given mouse button
    Move:   moves the mouse cursor by the given amount
    Scroll: scrolls the mouse wheel by the given amount"""

POINTER_CLICK_BUTTONS = [
    {"name": "Left", "value": "left"},
    {"name": "Right", "value": "right"},
    {"name": "Middle", "value": "middle"},
    {"name": "Back", "value": "back"},
    {"name": "Forward", "value": "forward"},
    {"name": "Extra", "value": "extra"},
    {"name": "Side", "value": "side"},
]

CONFIG_KEY_POINTER_BUTTON = "button"
CONFIG_KEY_POINTER_DX = "dx"
CONFIG_KEY_POINTER_DY = "dy"

# Toplevel Domain
CONFIG_KEY_TOPLEVEL_ACTION = "toplevel_action"
TOPLEVEL_COMMAND_ACTIONS = [
    {"name": "Minimize", "value": "minimize"},
    {"name": "Maximize", "value": "maximize"},
    {"name": "Fullscreen", "value": "fullscreen"},
    {"name": "Focus", "value": "focus"},
]
TOPLEVEL_COMMAND_ACTIONS_INSTRUCTIONS = """
    Minimize: Minimizes the matching clients
    Maximize: Maximizes the matching clients
    Fullscreen: Makes the matching clients fullscreen
    Focus: Focuses the matching clients"""

TOPLEVEL_SENSOR_ACTIONS = [
    {"name": "Find", "value": "find"},
    # {"name": "Wait", "value": "wait"},
    # {"name": "Waitfor", "value": "waitfor"},
]
TOPLEVEL_SENSOR_ACTIONS_INSTRUCTIONS = """
    Find: returns True if atleast one matching client is present"""

CONFIG_KEY_TOPLEVEL_APP_ID = "app_id"
CONFIG_KEY_TOPLEVEL_STATE = "state"
CONFIG_KEY_TOPLEVEL_TITLE = "title"

TOPLEVEL_STATE_CHOICES = [
    {"name": "Fullscreen", "value": "fullscreen"},
    {"name": "Maximized", "value": "maximized"},
    {"name": "Minimized", "value": "minimized"},
    {"name": "Active", "value": "active"},
    {"name": "Inactive", "value": "inactive"},
    {"name": "Unmaximized", "value": "unmaximized"},
    {"name": "Unminimized", "value": "unminimized"},
    {"name": "Unfullscreen", "value": "unfullscreen"},
    {"name": "None", "value": "none"},
]

# Output Domain
CONFIG_KEY_OUTPUT_ACTION = "output_action"
OUTPUT_ACTIONS = [
    {"name": "List", "value": "list"},
]
OUTPUT_ACTIONS_INSTRUCTIONS = """
    List: lists all connected monitor outputs"""


class Wlrctl(Entity):
    """Entity to control Wayland compositor"""

    NAME = "Wlrctl"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.domain: str = ""
        self.action: str = ""
        self.keys: str = ""
        self.modifiers: str = ""
        self.button: str = ""
        self.dx: int = ""
        self.dy: int = ""
        self.command: str = ""
        self.matchspec: str = ""
        self.hasValue: bool = ""
        self.isCommand = ""
        self.detection = ""
        self.state = ""
        self.isBinarySensor = ""
        self.valueFormatterOptions = None
        self.customPaylod = {}
        self.hasExtraAttributes = None

        self.domain = self.GetFromConfigurations(CONFIG_KEY_DOMAIN)
        self.Log(self.LOG_DEBUG, f"initializing wlrctl {self.domain}")
        # Update the NAME
        name_extension = f"{self.domain.capitalize()}"
        self.NAME += name_extension

        # get the configuration depending on the domain
        if self.domain == "keyboard":
            self.action = self.GetFromConfigurations(CONFIG_KEY_KEYBOARD_ACTION)
            self.isCommand = True
            if self.action == "type":
                self.keys = self.GetFromConfigurations(CONFIG_KEY_KEYBOARD_KEYS)
                # self.modifiers = self.GetFromConfigurations(
                #     CONFIG_KEY_KEYBOARD_MODIFIERS
                # )
                # build the command, add modifiers if needed
                if (
                    " " in self.keys
                ):  # if there is a space in the string, wrap it in quotes
                    self.command = f"wlrctl {self.domain} {self.action} '{self.keys}'"
                else:
                    self.command = f"wlrctl {self.domain} {self.action} {self.keys}"
                if self.modifiers:
                    self.command += f"modifiers {self.modifiers}"
            else:
                self.Log(
                    self.LOG_DEBUG, f"Keyboard Action {self.action} not implemented"
                )
                raise Exception("Action not implemented")

        elif self.domain == "pointer":
            self.action = self.GetFromConfigurations(CONFIG_KEY_POINTER_ACTION)
            self.isCommand = True
            if self.action == "click":
                self.button = self.GetFromConfigurations(CONFIG_KEY_POINTER_BUTTON)
                self.command = f"wlrctl {self.domain} {self.action} {self.button}"
            elif self.action == "move":
                self.dx = self.GetFromConfigurations(CONFIG_KEY_POINTER_DX)
                self.dy = self.GetFromConfigurations(CONFIG_KEY_POINTER_DY)
                self.command = f"wlrctl {self.domain} {self.action} {self.dx} {self.dy}"
            elif self.action == "scroll":
                self.dx = self.GetFromConfigurations(CONFIG_KEY_POINTER_DX)
                self.dy = self.GetFromConfigurations(CONFIG_KEY_POINTER_DY)
                self.command = f"wlrctl {self.domain} {self.action} {self.dy} {self.dx}"
            else:
                self.Log(
                    self.LOG_DEBUG, f"Pointer Action {self.action} not implemented"
                )
                raise Exception("Action not implemented")

        elif self.domain == "toplevelcommand" or self.domain == "toplevelsensor":
            if self.domain == "toplevelcommand":
                self.isCommand = True
            elif self.domain == "toplevelsensor":
                self.isBinarySensor = True
            self.domain = "toplevel"
            self.action = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_ACTION)
            # check if the action is implemented generate it from a list comprehension of TOPLEVEL_COMMAND_ACTIONS

            if self.action not in [
                action["value"]
                for action in TOPLEVEL_COMMAND_ACTIONS + TOPLEVEL_SENSOR_ACTIONS
            ]:
                self.Log(
                    self.LOG_DEBUG, f"Toplevel Action {self.action} not implemented"
                )
                raise Exception("Action not implemented")

            app_id = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_APP_ID)
            title = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_TITLE)
            state = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_STATE)
            if app_id:  # TODO space handling is not pretty
                if " " in app_id:
                    self.matchspec += f"app_id:'{app_id}'"
                else:
                    self.matchspec += f"app_id:{app_id}"
            if title:
                if " " in title:
                    self.matchspec += f" title:'{title}'"
                else:
                    self.matchspec += f" title:{title}"
            if state:
                if " " in state:
                    self.matchspec += f" state:'{state}'"
                else:
                    self.matchspec += f" state:{state}"
            self.command = f"wlrctl {self.domain} {self.action} {self.matchspec}"

        elif self.domain == "output":
            self.hasExtraAttributes = True
            self.action = self.GetFromConfigurations(CONFIG_KEY_OUTPUT_ACTION)
            self.command = f"wlrctl {self.domain} {self.action}"

        if self.isCommand:
            self.RegisterEntityCommand(
                EntityCommand(self, KEY, self.Callback, KEY_STATE)
            )

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_STATE,
                supportsExtraAttributes=True,
                valueFormatterOptions=self.valueFormatterOptions,
                customPayload=self.customPaylod,
            )
        )

    def Update(self):
        if self.isBinarySensor:
            self.Log(self.LOG_DEBUG, f"Running {self.command}")
            command = self.RunCommand(self.command)
            self.detection = STATE_ON if command.returncode == 0 else STATE_OFF
            self.SetEntitySensorValue(KEY_STATE, self.detection)
        elif self.hasExtraAttributes:
            self.Log(self.LOG_DEBUG, f"Running {self.command}")
            command = self.RunCommand(self.command, timeout=1)
            # output = check_output(["wlrctl", "output", "list"],stderr=STDOUT, timeout=1)
            # self.Log(self.LOG_DEBUG, output)
            self.SetEntitySensorValue(KEY_STATE, STATE_ON)
            self.SetEntitySensorExtraAttribute(
                KEY_STATE,
                "Output",
                command.stdout
                #output
            )
                


    def Callback(self, message=None):
        self.Log(self.LOG_DEBUG, f"Running {self.command}")
        callbackProcess = self.RunCommand(self.command)
        if callbackProcess.returncode != 0:
            self.Log(self.LOG_ERROR, f"Error running {self.command}")
            self.SetEntitySensorExtraAttribute(
                KEY_STATE,
                "Last command output",
                f"Error: {callbackProcess.stderr}"
                if callbackProcess.stderr
                else callbackProcess.stdout,
            )
        else:
            self.SetEntitySensorExtraAttribute(
                KEY_STATE,
                "Last command output",
                callbackProcess.stdout,
            )

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        preset.AddEntry(
            name="Select domain",
            key=CONFIG_KEY_DOMAIN,
            mandatory=True,
            question_type="select",
            choices=DOMAIN_CHOICES,
        )

        #
        # keyboard domain
        #
        preset.AddEntry(
            name="Select keyboard action",
            key=CONFIG_KEY_KEYBOARD_ACTION,
            instruction=KEYBOARD_ACTIONS_INSTRUCTIONS,
            mandatory=True,
            question_type="select",
            choices=KEYBOARD_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "keyboard"},
        )

        preset.AddEntry(
            name="Which string should be sent?",
            instruction=KEYBOARD_ACTIONS_INSTRUCTIONS,
            key=CONFIG_KEY_KEYBOARD_KEYS,
            mandatory=True,
            question_type="text",
            display_if_key_value={CONFIG_KEY_KEYBOARD_ACTION: "type"},
        )
        # TODO modifiers work janky in my testing
        # ask yes or no for modifiers
        # preset.AddEntry(
        #     name="Should a modifier be used?",
        #     key=CONFIG_KEY_KEYBOARD_MODIFIERS_YES,
        #     mandatory=True,
        #     question_type="yesno",
        #     choices=POINTER_ACTIONS,
        #     display_if_key_value={CONFIG_KEY_KEYBOARD_ACTION: "type"},
        # )
        # asking for multiple modifiers requires ability to select multiple choices TODO
        # preset.AddEntry(
        #     name="Select keyboard modifiers",
        #     key=CONFIG_KEY_KEYBOARD_MODIFIERS,
        #     mandatory=True,
        #     question_type="select",
        #     choices=KEYBOARD_MODIFIERS,
        #     display_if_key_value={CONFIG_KEY_KEYBOARD_MODIFIERS_YES: "Y"},
        # )

        #
        # pointer domain
        #
        preset.AddEntry(
            name="Select pointer action",
            key=CONFIG_KEY_POINTER_ACTION,
            instruction=POINTER_ACTIONS_INSTRUCTIONS,
            mandatory=True,
            question_type="select",
            choices=POINTER_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "pointer"},
        )
        #
        # click
        #
        preset.AddEntry(
            name="Select button",
            key=CONFIG_KEY_POINTER_BUTTON,
            choices=POINTER_CLICK_BUTTONS,
            mandatory=True,
            question_type="select",
            display_if_key_value={CONFIG_KEY_POINTER_ACTION: "click"},
        )

        #
        # move
        #
        for direction in ["x", "y"]:
            preset.AddEntry(
                name=f"How much moving in {direction}-direction",
                key=CONFIG_KEY_POINTER_DX
                if direction == "x"
                else CONFIG_KEY_POINTER_DY,
                mandatory=True,
                question_type="integer",
                display_if_key_value={CONFIG_KEY_POINTER_ACTION: "move"},
            )
        #
        # scroll
        #
        for direction in ["x", "y"]:
            preset.AddEntry(
                name=f"How much scrolling in {direction}-direction",
                key=CONFIG_KEY_POINTER_DY
                if direction == "y"
                else CONFIG_KEY_POINTER_DX,
                mandatory=True,
                question_type="integer",
                display_if_key_value={CONFIG_KEY_POINTER_ACTION: "scroll"},
            )

        #
        # toplevelcommand domain
        #
        preset.AddEntry(
            name="Select toplevel action",
            key=CONFIG_KEY_TOPLEVEL_ACTION,
            instruction=TOPLEVEL_COMMAND_ACTIONS_INSTRUCTIONS,
            mandatory=True,
            question_type="select",
            choices=TOPLEVEL_COMMAND_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "toplevelcommand"},
        )
        #
        # toplevelsensor domain
        #
        preset.AddEntry(
            name="Select toplevel sensor",
            key=CONFIG_KEY_TOPLEVEL_ACTION,
            instruction=TOPLEVEL_SENSOR_ACTIONS_INSTRUCTIONS,
            mandatory=True,
            question_type="select",
            choices=TOPLEVEL_SENSOR_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "toplevelsensor"},
        )
        for domain in ["toplevelcommand", "toplevelsensor"]:
            preset.AddEntry(
                name="Matchspec app_id?",
                key=CONFIG_KEY_TOPLEVEL_APP_ID,
                question_type="text",
                display_if_key_value={CONFIG_KEY_DOMAIN: domain},
            )
            preset.AddEntry(
                name="Matchspec title?",
                key=CONFIG_KEY_TOPLEVEL_TITLE,
                question_type="text",
                display_if_key_value={CONFIG_KEY_DOMAIN: domain},
            )
            preset.AddEntry(
                name="Matchspec state",
                key=CONFIG_KEY_TOPLEVEL_STATE,
                question_type="select",
                choices=TOPLEVEL_STATE_CHOICES,
                display_if_key_value={CONFIG_KEY_DOMAIN: domain},
            )

        #
        # output domain
        #
        preset.AddEntry(
            name="Select output action",
            key=CONFIG_KEY_OUTPUT_ACTION,
            instruction=OUTPUT_ACTIONS_INSTRUCTIONS,
            mandatory=True,
            question_type="select",
            choices=OUTPUT_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "output"},
        )

        return preset

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            pass
        else:
            raise NotImplementedError("Wlrctl is only supported on Linux")
