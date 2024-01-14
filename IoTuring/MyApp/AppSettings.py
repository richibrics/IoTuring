from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Logger.Logger import Singleton


CONFIG_KEY_UPDATE_INTERVAL = "update_interval"
CONFIG_KEY_SLOW_INTERVAL = "slow_interval"



class AppSettings(ConfiguratorObject, metaclass=Singleton):
    """Singleton for storing AppSettings, not related to Entites or Warehouses """
    NAME = "AppSettings"

    def __init__(self) -> None:
        pass


    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        preset.AddEntry(name="Main update interval in seconds",
                        key=CONFIG_KEY_UPDATE_INTERVAL, mandatory=True,
                        question_type="integer", default=10)

        # preset.AddEntry(name="Secondary update interval in minutes",
        #                 key=CONFIG_KEY_SLOW_INTERVAL, mandatory=True,
        #                 question_type="integer", default=10)

        return preset
