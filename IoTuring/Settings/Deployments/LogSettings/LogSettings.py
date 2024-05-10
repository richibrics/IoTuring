from pathlib import Path

from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Settings.Settings import Settings
from IoTuring.Logger.Logger import Logger
from IoTuring.Configurator.Configuration import SingleConfiguration
from IoTuring.MyApp.App import App
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Logger.LogLevel import LogLevel
from IoTuring.Logger import consts


# macOS dep (in PyObjC)
try:
    from AppKit import *  # type:ignore
    from Foundation import *  # type:ignore
    macos_support = True
except:
    macos_support = False


CONFIG_KEY_CONSOLE_LOG_LEVEL = "console_log_level"
CONFIG_KEY_CONSOLE_LOG_TIME = "console_log_time"
CONFIG_KEY_FILE_LOG_LEVEL = "file_log_level"
CONFIG_KEY_FILE_LOG_ENABLED = "file_log_enabled"
CONFIG_KEY_FILE_LOG_PATH = "file_log_path"


all_loglevels = sorted(Logger.GetLoglevels(), key=lambda l: int(l))

loglevel_choices = [{"name": str(l).capitalize(), "value": str(l)}
                    for l in all_loglevels]


class LogSettings(Settings):
    NAME = "Log"

    def __init__(self, single_configuration: SingleConfiguration, early_init: bool) -> None:
        super().__init__(single_configuration, early_init)

        # Load settings to logger:
        logger = Logger()

        logger.SetupConsoleLogging(
            loglevel=LogLevel(
                self.GetFromConfigurations(CONFIG_KEY_CONSOLE_LOG_LEVEL)),
            include_time=self.GetTrueOrFalseFromConfigurations(
                CONFIG_KEY_CONSOLE_LOG_TIME)
        )

        logger.SetupFileLogging(
            enabled=self.GetTrueOrFalseFromConfigurations(
                CONFIG_KEY_FILE_LOG_ENABLED),
            loglevel=LogLevel(self.GetFromConfigurations(
                CONFIG_KEY_FILE_LOG_LEVEL)),
            log_dir_path=Path(self.GetFromConfigurations(
                CONFIG_KEY_FILE_LOG_PATH)),
            early_init=early_init
        )

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        preset.AddEntry(name="Console log level", key=CONFIG_KEY_CONSOLE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=str(LogLevel(consts.DEFAULT_LOG_LEVEL)),
                        instruction="IOTURING_LOG_LEVEL envvar overwrites this setting!",
                        choices=loglevel_choices)

        preset.AddEntry(name="Display time in console log", key=CONFIG_KEY_CONSOLE_LOG_TIME,
                        question_type="yesno", default="Y")

        preset.AddEntry(name="Enable file logging", key=CONFIG_KEY_FILE_LOG_ENABLED,
                        question_type="yesno", default="N")

        preset.AddEntry(name="File log level", key=CONFIG_KEY_FILE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=str(LogLevel(consts.DEFAULT_LOG_LEVEL)),
                        choices=loglevel_choices, display_if_key_value={CONFIG_KEY_FILE_LOG_ENABLED: "Y"})

        preset.AddEntry(name="File log path", key=CONFIG_KEY_FILE_LOG_PATH,
                        question_type="filepath", mandatory=True, default=cls.GetDefaultLogPath(),
                        instruction="Directory where log files will be saved",
                        display_if_key_value={CONFIG_KEY_FILE_LOG_ENABLED: "Y"})

        return preset

    @staticmethod
    def GetDefaultLogPath() -> str:

        default_path = App.getRootPath().joinpath(
            "Logger").joinpath(consts.LOGS_FOLDER)
        base_path = None

        if OsD.IsMacos() and macos_support:
            base_path = \
                Path(NSSearchPathForDirectoriesInDomains(  # type: ignore
                    NSLibraryDirectory,  # type: ignore
                    NSUserDomainMask, True)[0])  # type: ignore
        elif OsD.IsWindows():
            base_path = Path(OsD.GetEnv("LOCALAPPDATA"))
        elif OsD.IsLinux():
            if OsD.GetEnv("XDG_CACHE_HOME"):
                base_path = Path(OsD.GetEnv("XDG_CACHE_HOME"))
            elif OsD.GetEnv("HOME"):
                base_path = Path(OsD.GetEnv("HOME")).joinpath(".cache")

        if base_path:
            default_path = base_path.joinpath(App.getName())

        return str(default_path)
