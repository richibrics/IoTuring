from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Configurator.MenuPreset import MenuPreset

from IoTuring.Logger import consts

CONFIG_KEY_CONSOLE_LOG_LEVEL = "console_log_level"
CONFIG_KEY_FILE_LOG_LEVEL = "console_file_level"


CONFIG_KEY_UPDATE_INTERVAL = "update_interval"
CONFIG_KEY_SLOW_INTERVAL = "slow_interval"

DEFAULT_LOG_LEVEL = "LOG_INFO"

LogLevelChoices = [{"name": l["string"], "value": l["const"]}
                   for l in consts.LOG_LEVELS]
# LogLevelChoices = [l["const"] for l in consts.LOG_LEVELS]


class AppSettings(ConfiguratorObject):
    # Default log levels, so Logging can start before configuration is loaded
    Settings = {
        CONFIG_KEY_CONSOLE_LOG_LEVEL: DEFAULT_LOG_LEVEL,
        CONFIG_KEY_FILE_LOG_LEVEL: DEFAULT_LOG_LEVEL
    }

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        preset.AddEntry(name="Console log level", key=CONFIG_KEY_CONSOLE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=DEFAULT_LOG_LEVEL,
                        instruction="IOTURING_LOG_LEVEL envvar overwrites this setting!",
                        choices=LogLevelChoices)

        preset.AddEntry(name="File log level", key=CONFIG_KEY_FILE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=DEFAULT_LOG_LEVEL,
                        choices=LogLevelChoices)

        preset.AddEntry(name="Main update interval in seconds",
                        key=CONFIG_KEY_UPDATE_INTERVAL, mandatory=True,
                        question_type="text", default="10")

        preset.AddEntry(name="Secondary update interval in minutes",
                        key=CONFIG_KEY_SLOW_INTERVAL, mandatory=True,
                        question_type="text", default="10")

        return preset
