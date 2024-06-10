from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Settings.SettingsManager import SettingsManager
from IoTuring.Configurator.MenuPreset import BooleanAnswers
from IoTuring.Configurator.Configuration import SingleConfiguration


class Settings(ConfiguratorObject):
    """Base class for settings"""
    NAME = "Settings"

    def __init__(self, single_configuration: SingleConfiguration, early_init: bool) -> None:
        """Initialize a settings class

        Args:
            single_configuration (SingleConfiguration): The configuration
            early_init (bool): True when loaded before configurator menu, False when added to SettingsManager
        """
        super().__init__(single_configuration)

    @classmethod
    def GetFromSettingsConfigurations(cls, key: str):
        """Get value from settings' saved configurations from SettingsManager

        Args:
            key (str): The CONFIG_KEY of the configuration

        Raises:
            Exception: If the key not found

        Returns:
            Any: The config value
        """

        sM = SettingsManager()
        saved_config = sM.GetConfigOfType(cls)

        if saved_config.HasConfigKey(key):
            return saved_config.GetConfigValue(key)
        else:
            raise Exception(
                f"Can't find key {key} in SettingsManager configurations")

    @classmethod
    def GetTrueOrFalseFromSettingsConfigurations(cls, key: str) -> bool:
        """Get boolean value from settings' saved configurations from SettingsManager

        Args:
            key (str): The CONFIG_KEY of the configuration

        Returns:
            bool: The config value
        """

        value = cls.GetFromSettingsConfigurations(key).lower()
        return bool(value in BooleanAnswers.TRUE_ANSWERS)
