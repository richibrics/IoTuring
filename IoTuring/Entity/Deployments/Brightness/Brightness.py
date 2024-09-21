from pathlib import Path
import re
import sys

from IoTuring.Entity.Entity import Entity
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.EntityData import EntitySensor, EntityCommand
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De
from IoTuring.Entity.ValueFormat import ValueFormatterOptions


KEY_CMD = "command"
KEY_STATE = "state"
KEY_BRIGHTNESS = "value"

CONFIG_KEY_GPU = "gpu"


class BrightnessCmds:
    """Base class storing commands for setting and getting brightness.

        In child classes override _GetValue and _SetValue methods. 
            Value should be a string from/to this methods, 
            conversion to int and scaling happens in Get and Set methods.
    """

    def __init__(
        self,
        scale: float = 100,
        decimals: int = 0,
        set_command: str = "{}",
        get_command: str = "",
    ) -> None:
        """Set parameters for this platform

        Args:
            scale (float, optional): The maximum value of brightness. Defaults to 100.
            decimals (int, optional): Required decimals. Defaults to 0.
            set_command (str, optional): Terminal command to set brightness.
                "{}" will be replaced with brightness value. Defaults to "{}".
                Ignore with custom _SetValue method in subclasses.
            get_command (str, optional): Terminal command to get brightness. Defaults to "".
                Ignore with custom _GetValue method in subclasses.
        """
        self.scale = scale
        self.decimals = decimals
        self.set_command = set_command
        self.get_command = get_command

    def Set(self, value: int) -> None:
        if not 0 <= value <= 255:
            raise Exception("Invalid value")
        scaled_value = (value / 255) * self.scale
        scaled_value = round(scaled_value, self.decimals)
        scaled_value = int(
            scaled_value) if self.decimals == 0 else scaled_value
        self._SetValue(value_str=str(scaled_value))

    def _SetValue(self, value_str: str) -> None:
        command = self.set_command.format(value_str)
        OsD.RunCommand(command, shell=True)

    def Get(self) -> int:
        scaled_value = float(self._GetValue())
        value = (scaled_value / self.scale) * 255
        return int(value)

    def _GetValue(self) -> str:
        value_str = OsD.RunCommand(self.get_command).stdout
        return value_str

    @classmethod
    def CheckPlatformSupported(cls) -> None:
        raise NotImplementedError("Should be implemented in subclasses")

    @classmethod
    def AllowMultiInstance(cls) -> bool:
        return False


class Brightness_Macos(BrightnessCmds):
    # TODO needs to be tested
    def __init__(self) -> None:
        super().__init__(
            scale=1,
            decimals=2,
            set_command="brightness {}",
            get_command="brightness -l",
        )

    def _GetValue(self) -> str:
        stdout = super()._GetValue()
        brightness = re.findall("display 0: brightness.*$", stdout)[0][22:30]
        return brightness

    @classmethod
    def CheckPlatformSupported(cls) -> None:
        if not OsD.CommandExists("brightness"):
            raise Exception(
                "Brightness not available, have you installed 'brightness' on Homebrew ?"
            )


class Brightness_Win(BrightnessCmds):
    # TODO needs to be tested
    # TODO support multiple monitors
    def __init__(self, monitor_id: int = 0) -> None:
        super().__init__()

        import pythoncom  # type: ignore
        import wmi  # type: ignore

        pythoncom.CoInitialize()
        self.monitor_id = monitor_id
        self.wmi = wmi.WMI(namespace="wmi")

    def _SetValue(self, value_str: str) -> None:
        self.wmi.WmiMonitorBrightnessMethods()[self.monitor_id].WmiSetBrightness(
            int(value_str), 0
        )

    def _GetValue(self) -> str:
        return self.wmi.WmiMonitorBrightness()[self.monitor_id].CurrentBrightness

    @classmethod
    def CheckPlatformSupported(cls) -> None:
        if ["wmi", "pythoncom"] not in sys.modules:
            raise Exception(
                "Wmi or Pythoncom package missing"
            )


class Brightness_Linux_ACPI(BrightnessCmds):
    ROOT_PATH = Path("/sys/class/backlight")

    def __init__(self, configuredGPU: str) -> None:
        self.gpu_path = self.ROOT_PATH.joinpath(configuredGPU)
        scale = int(self.get_from_file("max_brightness"))
        super().__init__(scale=scale)

    def _SetValue(self, value_str: str) -> None:
        with open(self.gpu_path.joinpath("brightness"), "w") as file:
            file.write(f"{value_str}\n")

    def _GetValue(self) -> str:
        return self.get_from_file("brightness")

    def get_from_file(self, file_name: str) -> str:
        with open(self.gpu_path.joinpath(file_name), "r") as file:
            content = file.read()
            return content.strip("\n")

    @classmethod
    def get_gpus(cls) -> list[str]:
        return [str(d.name) for d in cls.ROOT_PATH.iterdir() if d.is_dir()]

    @classmethod
    def CheckPlatformSupported(cls) -> None:
        if not cls.ROOT_PATH.exists():
            raise Exception("ACPI: dir not found!")
        if not [f for f in cls.ROOT_PATH.iterdir()]:
            raise Exception("ACPI: No Gpu found!")

    @classmethod
    def AllowMultiInstance(cls) -> bool:
        return bool(len(cls.get_gpus()) > 1)


class Brightness_Linux_Gnome(BrightnessCmds):
    DBUS_COMMAND_TEMPLATE = " ".join(
        [
            "gdbus call --session",
            "--dest org.gnome.SettingsDaemon.Power",
            "--object-path /org/gnome/SettingsDaemon/Power",
            "--method org.freedesktop.DBus.Properties.{}",
            "org.gnome.SettingsDaemon.Power.Screen Brightness",
        ]
    )

    def __init__(self) -> None:

        super().__init__(
            set_command=self.DBUS_COMMAND_TEMPLATE.format(
                "Set") + ' "<int32 {}>"',
            get_command=self.DBUS_COMMAND_TEMPLATE.format("Get"),
        )

    def _GetValue(self) -> str:
        stdout = super()._GetValue()
        brightness = re.findall(r"<(\d*)", stdout)[0]
        return brightness

    @classmethod
    def CheckPlatformSupported(cls) -> None:
        stdout = OsD.RunCommand(cls.DBUS_COMMAND_TEMPLATE.format("Get")).stdout
        if not re.findall(r"<\d", stdout):
            raise Exception("Gnome: Dbus Brightness not supported!")


class Brightness(Entity):
    NAME = "Brightness"
    # ALLOW_MULTI_INSTANCE depends on platform. See AllowMultiInstance()

    brightness_cmds: BrightnessCmds

    def Initialize(self):
        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_STATE,
                valueFormatterOptions=ValueFormatterOptions(
                    value_type=ValueFormatterOptions.TYPE_BINARY
                ),
            )
        )
        self.RegisterEntitySensor(EntitySensor(self, KEY_BRIGHTNESS))
        self.RegisterEntityCommand(
            EntityCommand(
                self,
                KEY_CMD,
                self.Callback,
                connectedEntitySensorKeys=[KEY_STATE, KEY_BRIGHTNESS],
            )
        )

        command_class = self.GetCommandClass()
        if command_class == Brightness_Linux_ACPI:
            configuredGPU: str = self.GetFromConfigurations(CONFIG_KEY_GPU)
            self.brightness_cmds = Brightness_Linux_ACPI(configuredGPU)
        else:
            self.brightness_cmds = command_class()

    def Callback(self, message):
        state = message.payload.decode("utf-8")
        self.brightness_cmds.Set(int(state))

    def Update(self):
        value = self.brightness_cmds.Get()
        self.SetEntitySensorValue(KEY_BRIGHTNESS, value)
        self.SetEntitySensorValue(KEY_STATE, 1 if value > 0 else 0)

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        if cls.GetCommandClass() == Brightness_Linux_ACPI:
            gpus = Brightness_Linux_ACPI.get_gpus()

            if len(gpus) > 1:
                preset.AddEntry(
                    name="which GPUs backlight you want to control?",
                    key=CONFIG_KEY_GPU,
                    question_type="select",
                    choices=gpus,
                    default=gpus[0]
                )
            else:
                # Set default value, if only one gpu, hidden question:
                preset.AddEntry(
                    name="which GPUs backlight you want to control?",
                    key=CONFIG_KEY_GPU,
                    question_type="select",
                    choices=gpus,
                    default=gpus[0],
                    display_if_key_value={CONFIG_KEY_GPU: False}
                )

        return preset

    @classmethod
    def CheckSystemSupport(cls):
        cls.GetCommandClass()

    @classmethod
    def AllowMultiInstance(cls):
        return cls.GetCommandClass().AllowMultiInstance()

    @classmethod
    def GetCommandClass(cls) -> type:
        """Get Brightness Command class. Raises exception if not supported"""

        classes: list[type] = []
        exceptions: list[str] = []

        if OsD.IsWindows():
            classes.append(Brightness_Win)
        elif OsD.IsMacos():
            classes.append(Brightness_Macos)

        elif OsD.IsLinux():

            if De.GetDesktopEnvironment() == "gnome":
                classes.append(Brightness_Linux_Gnome)

            classes.append(Brightness_Linux_ACPI)

        else:
            raise cls.UnsupportedOsException()

        for cls in classes:
            try:
                cls.CheckPlatformSupported()
                return cls
            except Exception as e:
                exceptions.append(str(e))

        raise Exception(" ".join(exceptions))
