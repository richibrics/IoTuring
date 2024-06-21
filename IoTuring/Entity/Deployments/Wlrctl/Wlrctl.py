from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY = "wlrctl"
KEY_STATE = "wlrctl_state"


CONFIG_KEY_DOMAIN = "domain"
DOMAIN_CHOICES = [
    {"name": "Keyboard", "value": "keyboard"},
    {"name": "Pointer", "value": "pointer"},
    {"name": "ToplevelCommand", "value": "toplevelcommand"},
    {"name": "ToplevelSensor", "value": "toplevelsensor"},
]

CONFIG_KEY_KEYBOARD_ACTION = "keyboard_action"
KEYBOARD_ACTIONS = [
    {"name": "Type", "value": "type"},
]

TYPE_INSTRUCTION = """type <string> [modifiers]: Send a string to be typed \
    into the focused client\n\
    modifiers <SHIFT,CTRL,ALT,SUPER>: Comma separated list of modifiers to \
    be held while typing"""

CONFIG_KEY_KEYBOARD_KEYS = "keys"

CONFIG_KEY_KEYBOARD_MODIFIERS = "modifiers"
KEYBOARD_MODIFIERS = [
    {"name": "Shift", "value": "SHIFT"},
    {"name": "Ctrl", "value": "CTRL"},
    {"name": "Alt", "value": "ALT"},
    {"name": "Super", "value": "SUPER"},
]


CONFIG_KEY_POINTER_ACTION = "pointer_action"
POINTER_ACTIONS = [
    {"name": "Click", "value": "click"},
    {"name": "Move", "value": "move"},
    {"name": "Scroll", "value": "scroll"},
]
POINTER_CLICK_INSTRUCTIONS = (
    'buttons are "left", "right", "middle", "back", "forward", "exra", "side"'
)


CONFIG_KEY_POINTER_BUTTON = "button"
CONFIG_KEY_POINTER_DX = "dx"
CONFIG_KEY_POINTER_DY = "dy"


CONFIG_KEY_TOPLEVEL_ACTION = "toplevel_action"
TOPLEVEL_COMMAND_ACTIONS = [
    {"name": "Minimize", "value": "minimize"},
    {"name": "Maximize", "value": "maximize"},
    {"name": "Fullscreen", "value": "fullscreen"},
    {"name": "Focus", "value": "focus"},
]
TOPLEVEL_SENSOR_ACTIONS = [
    {"name": "Find", "value": "find"},
    {"name": "Wait", "value": "wait"},
    {"name": "Waitfor", "value": "waitfor"},
]

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

CONFIG_KEY_OUTPUT_ACTION = "output_action"
OUTPUT_ACTIONS = [
    {"name": "List", "value": "list"},
]
# actions are:
#   list - lists all known outputs


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

            if self.action not in [action["value"] for action in TOPLEVEL_COMMAND_ACTIONS + TOPLEVEL_SENSOR_ACTIONS]:
                self.Log(
                    self.LOG_DEBUG, f"Toplevel Action {self.action} not implemented"
                )
                raise Exception("Action not implemented")

            app_id = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_APP_ID)
            title = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_TITLE)
            state = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_STATE)
            if app_id:
                self.matchspec += f"app_id:{app_id}"
            if title:
                self.matchspec += f" title:{title}"
            if state:
                self.matchspec += f" state:{state}"
            self.command = f"wlrctl {self.domain} {self.action} {self.matchspec}"

        elif self.domain == "output":
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
            #TODO toplevel wait and waitfor are not implemented correctly, maybe too much work 

    def Callback(self, message):
        self.Log(self.LOG_DEBUG, f"Running {self.command}")
        callbackProcess = self.RunCommand(self.command)
        if callbackProcess.returncode != 0:
            self.Log(self.LOG_ERROR, f"Error running {self.command}")
            self.SetEntitySensorExtraAttribute(
                KEY_STATE,
                "Last command outout",
                f"Error: {callbackProcess.stderr}"
                if callbackProcess.stderr
                else callbackProcess.stdout,
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
            # instruction=TYPE_INSTRUCTION, # TODO too convoluted
            key=CONFIG_KEY_KEYBOARD_ACTION,
            mandatory=True,
            question_type="select",
            choices=KEYBOARD_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "keyboard"},
        )

        preset.AddEntry(
            name="Which string should be sent?",
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
            instruction=POINTER_CLICK_INSTRUCTIONS,
            mandatory=True,
            question_type="text",
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
            key=CONFIG_KEY_TOPLEVEL_ACTION,
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
