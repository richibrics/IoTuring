from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from IoTuring.Configurator.Configurator import Configurator

from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Logger.Logger import Singleton

from IoTuring.Logger.consts import LOG_LEVELS, DEFAULT_LOG_LEVEL

CONFIG_KEY_CONSOLE_LOG_LEVEL = "console_log_level"
CONFIG_KEY_FILE_LOG_LEVEL = "file_log_level"
CONFIG_KEY_FILE_LOG_ENABLED = "file_log_enabled"


CONFIG_KEY_UPDATE_INTERVAL = "update_interval"
CONFIG_KEY_SLOW_INTERVAL = "slow_interval"


LogLevelChoices = [{"name": l["string"], "value": l["const"]}
                   for l in LOG_LEVELS]


class AppSettings(ConfiguratorObject, metaclass=Singleton):
    """Singleton for storing AppSettings, not related to Entites or Warehouses """

    def __init__(self) -> None:
        pass

    def LoadConfiguration(self, configurator: "Configurator"):
        """ Load/update configurations to the singleton """
        self.configurations = configurator.config.GetAppSettings()
        self.AddMissingDefaultConfigs()

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        preset.AddEntry(name="Console log level", key=CONFIG_KEY_CONSOLE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=DEFAULT_LOG_LEVEL,
                        instruction="IOTURING_LOG_LEVEL envvar overwrites this setting!",
                        choices=LogLevelChoices)

        preset.AddEntry(name="Enable file logging", key=CONFIG_KEY_FILE_LOG_ENABLED,
                        question_type="yesno", mandatory=True, default="Y")

        preset.AddEntry(name="File log level", key=CONFIG_KEY_FILE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=DEFAULT_LOG_LEVEL,
                        choices=LogLevelChoices)

        preset.AddEntry(name="Main update interval in seconds",
                        key=CONFIG_KEY_UPDATE_INTERVAL, mandatory=True,
                        question_type="integer", default=10)

        preset.AddEntry(name="Secondary update interval in minutes",
                        key=CONFIG_KEY_SLOW_INTERVAL, mandatory=True,
                        question_type="integer", default=10)

        return preset
