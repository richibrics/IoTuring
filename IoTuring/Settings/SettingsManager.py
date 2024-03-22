from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from IoTuring.Settings.Settings import Settings
    from IoTuring.Configurator.Configuration import SingleConfiguration

from IoTuring.Logger.Logger import Singleton
from IoTuring.Logger.LogObject import LogObject


class SettingsManager(LogObject, metaclass=Singleton):
    """Singleton for storing configurations of Settings"""

    def __init__(self) -> None:
        self.setting_configs = {}

    def AddSettings(self, setting_entities: list[Settings]) -> None:
        """Add settings configuration

        Args:
            setting_entities (list[Settings]): The loaded settings classes
        """
        for setting_entity in setting_entities:
            self.setting_configs[setting_entity.NAME] = setting_entity.configurations

    def GetConfigOfType(self, setting_class) -> SingleConfiguration:
        """Get the configuration of a saved class. Raises exception if not found"""

        if setting_class.NAME in self.setting_configs:
            return self.setting_configs[setting_class.NAME]
        else:
            raise Exception(f"No settings config for {setting_class.NAME}")
