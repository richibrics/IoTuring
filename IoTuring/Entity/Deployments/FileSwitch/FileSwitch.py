from pathlib import Path

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Configurator.MenuPreset import MenuPreset

KEY_STATE = 'fileswitch_state'
KEY_CMD = 'fileswitch'

CONFIG_KEY_PATH = 'path'


class FileSwitch(Entity):
    NAME = "FileSwitch"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):

        try:
            self.config_path = self.GetConfigurations()[CONFIG_KEY_PATH]
        except Exception as e:
            raise Exception("Configuration error: " + str(e))

        self.RegisterEntitySensor(EntitySensor(self, KEY_STATE, True))
        self.RegisterEntityCommand(EntityCommand(
            self, KEY_CMD, self.Callback, KEY_STATE))

    def PostInitialize(self):
        pass

    def Callback(self, message):
        payloadString = message.payload.decode('utf-8')

        if payloadString == "True":
            Path(self.config_path).touch()

        elif payloadString == "False":
            Path(self.config_path).unlink(missing_ok=True)

        else:
            raise Exception('Incorrect payload!')

    def Update(self):
        self.SetEntitySensorValue(KEY_STATE,
                                  str(Path(self.config_path).exists()))
        
        extra = {}
        extra["Path"] = str(self.config_path)
        self.SetEntitySensorExtraAttributes(KEY_STATE, extra)

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Path to file?", CONFIG_KEY_PATH, mandatory=True)
        return preset
