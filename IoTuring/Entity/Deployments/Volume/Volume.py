import subprocess

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions

KEY_STATE = 'volume_state'
KEY_CMD = 'volume'

EXTRA_KEY_MUTED_OUTPUT = 'Muted output'
EXTRA_KEY_OUTPUT_VOLUME = 'Output volume'
EXTRA_KEY_INPUT_VOLUME = 'Input volume'
EXTRA_KEY_ALERT_VOLUME = 'Alert volume'
VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0 = ValueFormatterOptions(value_type=ValueFormatterOptions.TYPE_PERCENTAGE, decimals=0)

class Volume(Entity):
    NAME = "Volume"
    DEPENDENCIES = ["Os"]

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")
        
        if self.os == "macOS":        
            self.RegisterEntitySensor(EntitySensor(self, KEY_STATE, supportsExtraAttributes=True, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0))
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.CallbackMac, KEY_STATE))
        else:
            raise Exception("Currently working only on macOS")


    def Update(self):
        if self.os == "macOS":        
            self.UpdateMac()
    
    def CallbackMac(self, message):
        payloadString = message.payload.decode('utf-8')
        try:
            # parse the payload and get the volume number which is between 0 and 100
            volume = int(payloadString)
            if volume < 0 or volume > 100:
                raise Exception('Incorrect payload!')
            self.SetVolumeMac(volume)
        except Exception as e:
            raise Exception('Incorrect payload!')
        
    def SetVolumeMac(self, volume_level):
        subprocess.run(['osascript', '-e', f'set volume output volume {volume_level}'], check=True)

    def UpdateMac(self):
        # result like: output volume:44, input volume:89, alert volume:100, output muted:false
        result = subprocess.run(['osascript', '-e', 'get volume settings'], capture_output=True, text=True)
        result = result.stdout.strip().split(',')
        
        output_volume = result[0].split(':')[1]
        input_volume = result[1].split(':')[1]
        alert_volume = result[2].split(':')[1]
        output_muted = False if result[3].split(':')[1] == 'false' else True
        
        self.SetEntitySensorValue(KEY_STATE, output_volume)
        self.SetEntitySensorExtraAttribute(KEY_STATE, EXTRA_KEY_OUTPUT_VOLUME, output_volume, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0)
        self.SetEntitySensorExtraAttribute(KEY_STATE, EXTRA_KEY_INPUT_VOLUME, input_volume, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0)
        self.SetEntitySensorExtraAttribute(KEY_STATE, EXTRA_KEY_ALERT_VOLUME, alert_volume, valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE_ROUND0)
        self.SetEntitySensorExtraAttribute(KEY_STATE, EXTRA_KEY_MUTED_OUTPUT, output_muted)