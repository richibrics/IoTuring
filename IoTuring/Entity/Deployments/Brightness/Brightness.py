from pathlib import Path
from IoTuring.Entity.Entity import Entity
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.EntityData import EntitySensor, EntityCommand
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De
from IoTuring.Entity.ValueFormat import ValueFormatterOptions


import re
import os
import sys


KEY_CMD = "command"
KEY_STATE = "state"
KEY_BRIGHTNESS = "value"

CONFIG_KEY_GPU = "gpu"


class BrightnessCmds:
    def __init__(
        self,
        scale: float = 100,
        decimals: int = 0,
        set_command: str = "{}",
        get_command: str = "",
    ) -> None:
        self.scale = scale
        self.decimals = decimals
        self.set_command = set_command
        self.get_command = get_command

    def Set(self, value: int) -> None:
        if not 0 <= value <= 255:
            raise Exception("Invalid value")
        scaled_value = (value / 255) * self.scale
        scaled_value = round(scaled_value, self.decimals)
        scaled_value = int(scaled_value) if self.decimals == 0 else scaled_value
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


class Brightness_Macos(BrightnessCmds):
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


class Brightness_Win(BrightnessCmds):
    def __init__(self, monitor_id: int = 0) -> None:
        super().__init__()

        import pythoncom
        import wmi

        pythoncom.CoInitialize()
        self.monitor_id = monitor_id
        self.wmi = wmi.WMI(namespace="wmi")

    def _SetValue(self, value_str: str) -> None:
        self.wmi.WmiMonitorBrightnessMethods()[self.monitor_id].WmiSetBrightness(
            int(value_str), 0
        )

    def _GetValue(self) -> str:
        return self.wmi.WmiMonitorBrightness()[self.monitor_id].CurrentBrightness


class Brightness_Linux_ACPI(BrightnessCmds):
    def __init__(self, configuredGPU: str) -> None:
        self.gpu_path = Path(f"/sys/class/backlight/{configuredGPU}")
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


class Brightness_Linux_Gnome(BrightnessCmds):
    def __init__(self) -> None:
        dbus_command = " ".join(
            [
                "gdbus call --session",
                "--dest org.gnome.SettingsDaemon.Power",
                "--object-path /org/gnome/SettingsDaemon/Power",
                "--method org.freedesktop.DBus.Properties.{}",
                "org.gnome.SettingsDaemon.Power.Screen Brightness",
            ]
        )

        super().__init__(
            set_command=dbus_command.format("Set") + ' "<int32 {}>"',
            get_command=dbus_command.format("Get"),
        )

    def _GetValue(self) -> str:
        stdout = super()._GetValue()
        brightness = re.findall(r"<(\d*)", stdout)[0]
        return brightness


class Brightness(Entity):
    NAME = "Brightness"
    ALLOW_MULTI_INSTANCE = True

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

        if OsD.IsWindows():
            self.brightness_cmds = Brightness_Win()
        elif OsD.IsMacos():
            self.brightness_cmds = Brightness_Macos()
        elif OsD.IsLinux():
            if De.GetDesktopEnvironment() == "gnome":
                self.brightness_cmds = Brightness_Linux_Gnome()
            else:
                configuredGPU: str = self.GetFromConfigurations(CONFIG_KEY_GPU)
                self.brightness_cmds = Brightness_Linux_ACPI(configuredGPU)
        else:
            raise Exception("Unsupported OS!")

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
        if OsD.IsLinux():
            # find all GPUs in /sys/class/backlight by listing all directories
            gpus = [
                gpu
                for gpu in os.listdir("/sys/class/backlight")
                if os.path.isdir(f"/sys/class/backlight/{gpu}")
            ]

            preset.AddEntry(
                name="which GPUs backlight you want to control?",
                key=CONFIG_KEY_GPU,
                question_type="select",
                choices=gpus,
            )
        return preset

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsWindows():  # TODO needs to be tested
            # if wmi and pythoncom are not available, raise an exception
            if ["wmi", "pythoncom"] not in sys.modules:
                raise Exception(
                    "Brightness not available, have you installed 'wmi' on pip ?"
                )
        elif OsD.IsMacos():  # TODO needs to be tested
            if not OsD.CommandExists("brightness"):
                raise Exception(
                    "Brightness not avaidlable, have you installed 'brightness' on Homebrew ?"
                )
        elif OsD.IsLinux():
            if not Path("/sys/class/backlight").exists():
                # TODO check if this dir always exists
                raise Exception(
                    "Brightness not available, no backlight found in /sys/class/backlight"
                )
        else:
            raise cls.UnsupportedOsException()
