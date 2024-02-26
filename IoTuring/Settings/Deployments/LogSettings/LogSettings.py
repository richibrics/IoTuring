from pathlib import Path

from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Logger.Logger import Logger
from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Configurator.Configuration import SingleConfiguration
from IoTuring.MyApp.App import App
from IoTuring.Logger import consts
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD


# macOS dep (in PyObjC)
try:
    from AppKit import *  # type:ignore
    from Foundation import *  # type:ignore
    macos_support = True
except:
    macos_support = False


CONFIG_KEY_CONSOLE_LOG_LEVEL = "console_log_level"
CONFIG_KEY_FILE_LOG_LEVEL = "file_log_level"
CONFIG_KEY_FILE_LOG_ENABLED = "file_log_enabled"
CONFIG_KEY_FILE_LOG_PATH = "file_log_path"


LogLevelChoices = [{"name": l["string"], "value": l["const"]}
                   for l in consts.LOG_LEVELS]


class LogSettings(ConfiguratorObject):
    NAME = "Log"

    def __init__(self, single_configuration: SingleConfiguration) -> None:
        super().__init__(single_configuration)

        # Load settings to logger:
        logger = Logger()

        logger.SetConsoleLogLevel(
            self.GetFromConfigurations(CONFIG_KEY_CONSOLE_LOG_LEVEL))

        if self.GetTrueOrFalseFromConfigurations(CONFIG_KEY_FILE_LOG_ENABLED):
            try:
                logger.StartFileLogging(self.GetFromConfigurations(CONFIG_KEY_FILE_LOG_LEVEL),
                                        Path(self.GetFromConfigurations(CONFIG_KEY_FILE_LOG_PATH)))
            except:
                logger.DisableFileLogging()
        else:
            logger.DisableFileLogging()

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()

        preset.AddEntry(name="Console log level", key=CONFIG_KEY_CONSOLE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=consts.DEFAULT_LOG_LEVEL,
                        instruction="IOTURING_LOG_LEVEL envvar overwrites this setting!",
                        choices=LogLevelChoices)

        preset.AddEntry(name="Enable file logging", key=CONFIG_KEY_FILE_LOG_ENABLED,
                        question_type="yesno", default="N")

        preset.AddEntry(name="File log level", key=CONFIG_KEY_FILE_LOG_LEVEL,
                        question_type="select", mandatory=True, default=consts.DEFAULT_LOG_LEVEL,
                        choices=LogLevelChoices)

        preset.AddEntry(name="File log path", key=CONFIG_KEY_FILE_LOG_PATH,
                        question_type="filepath", mandatory=True, default=cls.GetDefaultLogPath(),
                        instruction="Directory where log files will be saved")

        return preset

    @staticmethod
    def GetDefaultLogPath() -> str:

        default_path = App.getRootPath().joinpath("Logger")
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

        return str(default_path.joinpath(consts.LOGS_FOLDER))
