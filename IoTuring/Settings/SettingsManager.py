from __future__ import annotations

from IoTuring.Logger.Logger import Singleton
from IoTuring.Configurator.ConfiguratorObject import ConfiguratorObject
from IoTuring.Configurator.Configuration import SingleConfiguration


class SettingsManager(ConfiguratorObject, metaclass=Singleton):
    """Singleton for storing configurations of Settings"""

    def __init__(self) -> None:
        self.configurations = SingleConfiguration()

    def AddSettings(self, setting_entities: list[ConfiguratorObject]) -> None:
        for setting_entity in setting_entities:

            conf_dict = setting_entity.GetConfigurations().ToDict(include_type=False)

            for conf_key, conf_value in conf_dict.items():
                self.GetConfigurations().UpdateConfigValue(conf_key, conf_value)
