from IoTuring.Entity.Entity import Entity
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON


KEY = "ydotool"
KEY_STATE = "ydotool_state"


CONFIG_KEY_CMD = "command"
CMD_CHOICES = [
    {"name": "Type", "value": "type"},
    {"name": "Key", "value": "key"},
    {"name": "Mousemove", "value": "mousemove"},
    {"name": "Mousewheel", "value": "mousewheel"},
    {"name": "Click", "value": "click"},
]

#
# type
#
CONFIG_KEY_TYPE_STRING = "type_string"
TYPE_OPTION_SUPPORT = ["d", "H", "D", "f", "e"]
CONFIG_KEY_TYPE_ESCAPE = "escape"
CONFIG_KEY_TYPE_HOLD = "hold"

#
# key
#
CONFIG_KEY_KEY = "keys"
KEY_OPTION_SUPPORT = ["d"]

#
# click
#
CONFIG_KEY_CLICK_BUTTON = "button"
CLICK_INSTRUCTION = """
0x00 - LEFT     0x03 - SIDE     0x06 - BACK         0x80 - Mouse up
0x01 - RIGHT    0x04 - EXTR     0x07 - TASK
0x02 - MIDDLE   0x05 - FORWARD  0x40 - Mouse down
"""
CLICK_OPTION_SUPPORT = ["-r", "-D"]

#
# mousemove/wheel
#
CONFIG_KEY_MOUSEMOVE_ABSOLUTE = "absolute"
CONFIG_KEY_MOUSEMOVE_X = "move_x"
CONFIG_KEY_MOUSEMOVE_Y = "move_y"
MOUSEMOVE_OPTION_SUPPORT = ["a", "x", "y"]
CONFIG_KEY_MOUSEWHEEL_Y = "wheel_y"
CONFIG_KEY_MOUSEWHEEL_X = "wheel_x"
MOUSEWHEEL_OPTION_SUPPORT = ["y", "x"]

#
# key
#
CONFIG_KEY_DELAY = "delay"
CONFIG_KEY_NEXT_DELAY = "next_delay"
CONFIG_KEY_REPEAT = "repeat"


class Ydotool(Entity):
    """Entity to control Wayland compositor with Ydotool"""

    NAME = "Ydotool"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.domain = ""
        self.action = ""
        self.keys = ""
        self.modifiers_yes = ""
        self.modifiers = ""
        self.button = ""
        self.dx = ""
        self.dy = ""
        self.windows = ""
        self.command = ""
        self.hasValue = False
        self.hasCommand = False
        self.state = ""

        self.domain = self.GetFromConfigurations(CONFIG_KEY_CMD)
        self.Log(self.LOG_DEBUG, f"initializing wlrctl {self.domain}")
        # get the configuration depending on the domain TODO refactor into a function
        if self.domain == "click":
            self.command = f"ydotool {self.domain}\
                    {self.GetFromConfigurations(CONFIG_KEY_CLICK_BUTTON)}\
                    -r {self.GetFromConfigurations(CONFIG_KEY_REPEAT)}\
                    -D {self.GetFromConfigurations(CONFIG_KEY_DELAY)}"
        elif self.domain == "mousemove":
            self.command = f"ydotool {self.domain}\
                    {'-a' if self.GetFromConfigurations(CONFIG_KEY_MOUSEMOVE_ABSOLUTE) == 'Y' else ''}\
                    -x {self.GetFromConfigurations(CONFIG_KEY_MOUSEMOVE_X)}\
                    -y {self.GetFromConfigurations(CONFIG_KEY_MOUSEMOVE_Y)}"
        elif self.domain == "mousewheel":
            self.command = f"ydotool mousemove\
                    {self.GetFromConfigurations(CONFIG_KEY_MOUSEWHEEL_X)}\
                    {self.GetFromConfigurations(CONFIG_KEY_MOUSEWHEEL_Y)}"
        elif self.domain == "type":
            self.command = f"ydotool {self.domain}\
                    {self.GetFromConfigurations(CONFIG_KEY_TYPE_STRING)}\
                    -d {self.GetFromConfigurations(CONFIG_KEY_DELAY)}\
                    -H {self.GetFromConfigurations(CONFIG_KEY_TYPE_HOLD)}\
                    -D {self.GetFromConfigurations(CONFIG_KEY_DELAY)}\
                    -e {self.GetFromConfigurations(CONFIG_KEY_TYPE_ESCAPE)}"
                     # {'-f' if self.GetFromConfigurations(CONFIG_KEY_TYPE_STRING) == 'f' else ''}" # TODO Filepath not supported
        elif self.domain == "key":
            self.command = f"ydotool {self.domain}\
                    {self.GetFromConfigurations(CONFIG_KEY_KEY)}\
                    -d {self.GetFromConfigurations(CONFIG_KEY_DELAY)}"
        else:
            self.Log(self.LOG_ERROR, "Invalid domain")

        self.RegisterEntitySensor(
            EntitySensor(self, KEY_STATE, supportsExtraAttributes=True)
        )

        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback, KEY_STATE))

    def Update(self):
        pass

    def Callback(self, message):
        self.Log(self.LOG_DEBUG, f"Running {self.command}")
        command = self.RunCommand(self.command)

        if command.returncode != 0:
            self.Log(self.LOG_ERROR, f"Error running {self.command}")
            return False

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        preset.AddEntry(
            name="Select domain",
            key=CONFIG_KEY_CMD,
            mandatory=True,
            question_type="select",
            choices=CMD_CHOICES,
        )

        #
        # click command
        #
        preset.AddEntry(
            name="Which button should be clicked? default LeftClick",
            key=CONFIG_KEY_CLICK_BUTTON,
            instruction=CLICK_INSTRUCTION,
            mandatory=True,
            default="0x00",
            question_type="text",
            display_if_key_value={CONFIG_KEY_CMD: "click"},
        )
        for option in CLICK_OPTION_SUPPORT:
            if option == "-r":
                preset.AddEntry(
                    name="How many times should the action be repeated?",
                    key=CONFIG_KEY_REPEAT,
                    default=0,
                    mandatory=True,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "click"},
                )
            elif option == "-D":
                preset.AddEntry(
                    name="Delay between input events (up/down), default 20ms?",
                    key=CONFIG_KEY_DELAY,
                    default=20,
                    mandatory=True,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "click"},
                )
            else:
                pass

        #
        # mousemove command
        #
        for option in MOUSEMOVE_OPTION_SUPPORT:
            if option == "a":
                preset.AddEntry(
                    name="Should the mouse move absolute?",
                    key=CONFIG_KEY_MOUSEMOVE_ABSOLUTE,
                    mandatory=True,
                    default="Y",
                    question_type="yesno",
                    display_if_key_value={CONFIG_KEY_CMD: "mousemove"},
                )
            elif option == "x" or "y":
                preset.AddEntry(
                    name=f"How much movement in the {option} direction",
                    key=globals()[f"CONFIG_KEY_MOUSEMOVE_{option.upper()}"],
                    mandatory=True,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "mousemove"},
                )
            else:
                pass

        #
        # mousewheel command
        #
        for option in MOUSEWHEEL_OPTION_SUPPORT:
            if option == "x" or "y":
                preset.AddEntry(
                    name=f"How much scrolling in the {option} direction",
                    key=globals()[f"CONFIG_KEY_MOUSEWHEEL_{option.upper()}"],
                    mandatory=True,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "mousewheel"},
                )
            else:
                pass

        #
        # type command
        #
        preset.AddEntry(
            name="Which strings should be sent?, you can send multiple and configure the delay between them by separating them with a space, if you want to have that space in there, encase your text in quotes",
            key=CONFIG_KEY_TYPE_STRING,
            mandatory=True,
            question_type="text",
            display_if_key_value={CONFIG_KEY_CMD: "type"},
        )
        for option in TYPE_OPTION_SUPPORT:
            if option == "d":
                preset.AddEntry(
                    name="Delay between keys? in ms, default 20ms",
                    key=CONFIG_KEY_DELAY,
                    mandatory=True,
                    default=20,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "type"},
                )
            elif option == "H":
                preset.AddEntry(
                    name="how long should each key be held? in ms, default 20 ms",
                    key=CONFIG_KEY_TYPE_HOLD,
                    mandatory=True,
                    default=20,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "type"},
                )
            elif option == "D":
                preset.AddEntry(
                    name="Delay between strings? in ms, default 0 ms",
                    key=CONFIG_KEY_NEXT_DELAY,
                    mandatory=True,
                    default=0,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "type"},
                )
            elif option == "f":  # filepath TODO
                pass  # file path not supported
            elif option == "e":
                preset.AddEntry(
                    name="Enable Escape?",
                    key=CONFIG_KEY_TYPE_ESCAPE,
                    mandatory=True,
                    default="Y",
                    question_type="yesno",
                    display_if_key_value={CONFIG_KEY_CMD: "type"},
                )
            else:
                pass

        #
        # key command
        #
        preset.AddEntry(
            name="Which key should be sent?",
            key=CONFIG_KEY_KEY,
            mandatory=True,
            question_type="text",
            display_if_key_value={CONFIG_KEY_CMD: "key"},
        )
        for option in KEY_OPTION_SUPPORT:
            if option == "d":
                preset.AddEntry(
                    name="Delay between keys? in ms, default 20ms",
                    key=CONFIG_KEY_DELAY,
                    mandatory=True,
                    default=20,
                    question_type="integer",
                    display_if_key_value={CONFIG_KEY_CMD: "key"},
                )
            else:
                pass

        return preset

    @classmethod
    def addRepeatEntry(cls, preset: MenuPreset, display_if_key_value=None):
        preset.AddEntry(
            name="How many times should the action be repeated?",
            key=CONFIG_KEY_REPEAT,
            mandatory=True,
            question_type="integer",
            display_if_key_value=display_if_key_value,
        )

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            if OsD.CommandExists("ydotool"):
                # debug = cls.RunCommand(cls, "ydotool debug") TODO
                # somehow check if the daemon is running
                # if debug.returncode != 0:
                #    cls.Log(cls.LOG_ERROR, "ydotool has some issues")
                #    raise Exception("ydotool has some issues")
                return True
            else:
                cls.Log(cls.LOG_ERROR, "ydotool is not installed")
                raise Exception("ydotool is not installed")

        else:
            raise cls.UnsupportedOsException("ydotool is only supported on Linux")
