import subprocess
import re

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_STATE = 'volume_state'
KEY_CMD = 'volume'

EXTRA_KEY_MUTED_OUTPUT = 'Muted output'
EXTRA_KEY_OUTPUT_VOLUME = 'Output volume'
EXTRA_KEY_INPUT_VOLUME = 'Input volume'
EXTRA_KEY_ALERT_VOLUME = 'Alert volume'
VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0 = ValueFormatterOptions(
    value_type=ValueFormatterOptions.TYPE_PERCENTAGE, decimals=0)

commands = {
    OsD.OS_FIXED_VALUE_LINUX: 'pactl set-sink-volume @DEFAULT_SINK@ {}%',
    OsD.OS_FIXED_VALUE_MACOS: 'osascript -e "set volume output volume {}"'
}


class Volume(Entity):
    NAME = "Volume"

    def Initialize(self):
        extra_attributes = False

        if OsD.IsLinux():
            if not OsD.CommandExists("pactl"):
                raise Exception(
                    "Only PulseAudio is supported on Linux! Please open an issue on Github!")
        elif OsD.IsMacos():
            extra_attributes = True
        else:
            raise Exception("System not supported!")

        # Register:
        self.RegisterEntitySensor(EntitySensor(
            self, KEY_STATE,
            supportsExtraAttributes=extra_attributes,  # Extra attributes only on macos
            valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0))
        self.RegisterEntityCommand(EntityCommand(
            self, KEY_CMD, self.Callback, KEY_STATE))

    def Update(self):
        if OsD.IsMacos():
            self.UpdateMac()
        elif OsD.IsLinux():
            # Example: 'Volume: front-left: 39745 /  61% / -13,03 dB,   ... 
            # Only care about the first percent.
            p = subprocess.run("pactl get-sink-volume @DEFAULT_SINK@",
                               capture_output=True, shell=True, text=True)
            self.Log(self.LOG_DEBUG, f"pactl stdout: {p.stdout}")
            m = re.search(r"/ +(\d{1,3})% /", p.stdout)
            if m:
                volume = m.group(1)
                self.SetEntitySensorValue(KEY_STATE, volume)

    def Callback(self, message):
        payloadString = message.payload.decode('utf-8')

        # parse the payload and get the volume number which is between 0 and 100
        volume = int(payloadString)
        if not 0 <= volume <= 100:
            raise Exception('Incorrect payload!')
        else:
            subprocess.run(
                commands[OsD.GetOs()].format(volume),
                shell=True, check=True)

    def UpdateMac(self):
        # result like: output volume:44, input volume:89, alert volume:100, output muted:false
        result = subprocess.run(
            ['osascript', '-e', 'get volume settings'], capture_output=True, text=True)
        result = result.stdout.strip().split(',')

        output_volume = result[0].split(':')[1]
        input_volume = result[1].split(':')[1]
        alert_volume = result[2].split(':')[1]
        output_muted = False if result[3].split(':')[1] == 'false' else True

        self.SetEntitySensorValue(KEY_STATE, output_volume)
        self.SetEntitySensorExtraAttribute(
            KEY_STATE, EXTRA_KEY_OUTPUT_VOLUME, output_volume, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0)
        self.SetEntitySensorExtraAttribute(
            KEY_STATE, EXTRA_KEY_INPUT_VOLUME, input_volume, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0)
        self.SetEntitySensorExtraAttribute(
            KEY_STATE, EXTRA_KEY_ALERT_VOLUME, alert_volume, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0)
        self.SetEntitySensorExtraAttribute(
            KEY_STATE, EXTRA_KEY_MUTED_OUTPUT, output_muted)
