from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Settings.Settings import Settings


CONFIG_KEY_UPDATE_INTERVAL = "update_interval"
# CONFIG_KEY_SLOW_INTERVAL = "slow_interval"


class AppSettings(Settings):
    """Singleton for storing AppSettings, not related to a specifuc Entity or Warehouse """
    NAME = "App"

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
