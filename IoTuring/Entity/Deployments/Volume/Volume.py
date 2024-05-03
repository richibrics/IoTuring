import re

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
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
    OsD.LINUX: 'pactl set-sink-volume @DEFAULT_SINK@ {}%',
    OsD.MACOS: 'osascript -e "set volume output volume {}"'
}

UNMUTE_PREFIX_LINUX = 'pactl set-sink-mute @DEFAULT_SINK@ 0'


class Volume(Entity):
    NAME = "Volume"

    def Initialize(self):

        # Register:
        self.RegisterEntitySensor(EntitySensor(
            self, KEY_STATE,
            supportsExtraAttributes=True,
            valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0))
        self.RegisterEntityCommand(EntityCommand(
            self, KEY_CMD, self.Callback, KEY_STATE))

    def Update(self):
        if OsD.IsMacos():
            self.UpdateMac()
        elif OsD.IsLinux():
            # Check if it's muted:
            p = self.RunCommand(command="pactl get-sink-mute @DEFAULT_SINK@",
                                        shell=True)
            output_muted = bool(re.search("Mute: yes", p.stdout))

            if output_muted:
                output_volume = 0

            else:
                # Example: 'Volume: front-left: 39745 /  61% / -13,03 dB,   ...
                # Only care about the first percent.
                p = self.RunCommand(command="pactl get-sink-volume @DEFAULT_SINK@",
                                            shell=True)
                m = re.search(r"/ +(\d{1,3})% /", p.stdout)

                if not m:
                    raise Exception(f"Error getting volume from {p.stdout}")

                output_volume = m.group(1)

            self.SetEntitySensorValue(KEY_STATE, output_volume)
            self.SetEntitySensorExtraAttribute(
                KEY_STATE, EXTRA_KEY_MUTED_OUTPUT, output_muted)

    def Callback(self, message):
        payloadString = message.payload.decode('utf-8')

        # parse the payload and get the volume number which is between 0 and 100
        volume = int(payloadString)
        if not 0 <= volume <= 100:
            raise Exception('Incorrect payload!')

        cmd = commands[OsD.GetOs()]

        # Unmute on Linux:
        if 0 < volume and OsD.IsLinux():
            cmd = UNMUTE_PREFIX_LINUX + " && " + cmd

        self.RunCommand(command=cmd.format(volume),
                        shell=True)

    def UpdateMac(self):
        # result like: output volume:44, input volume:89, alert volume:100, output muted:false
        command = self.RunCommand(
            command=['osascript', '-e', 'get volume settings'])
        result = command.stdout.strip().split(',')

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

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            if not OsD.CommandExists("pactl"):
                raise Exception(
                    "Only PulseAudio is supported on Linux! Please open an issue on Github!")
        elif not OsD.IsMacos():
            raise cls.UnsupportedOsException()
