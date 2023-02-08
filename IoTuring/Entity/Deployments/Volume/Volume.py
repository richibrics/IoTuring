import subprocess

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor

KEY_STATE = 'volume_state'
KEY_CMD = 'volume'

class Volume(Entity):
    NAME = "Volume"
    ALLOW_MULTI_INSTANCE = True
    DEPENDENCIES = ["Os"]

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")
        self.getStateMethod = None
        
        if self.os == "macOS":        
            self.RegisterEntitySensor(EntitySensor(self, KEY_STATE, False))
            self.RegisterEntityCommand(EntityCommand(
                self, KEY_CMD, self.CallbackMac, KEY_STATE))
            self.getStateMethod = self.GetVolumeMac
        else:
            raise Exception("Currently working only on macOS")

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

    def GetVolumeMac(self):
        result = subprocess.run(['osascript', '-e', 'output volume of (get volume settings)'], capture_output=True, text=True)
        return int(result.stdout.strip())

    def Update(self):
        self.SetEntitySensorValue(KEY_STATE, self.getStateMethod())