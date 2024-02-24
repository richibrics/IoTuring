from IoTuring.Configurator.MenuPreset import BooleanAnswers, MenuPreset
from IoTuring.Configurator.Configuration import SingleConfiguration


class ConfiguratorObject:
    """ Base class for configurable classes """
    NAME = "Unnamed"

    def __init__(self, single_configuration: SingleConfiguration) -> None:
        self.configurations = single_configuration

        # Add missing default values:
        preset = self.ConfigurationPreset()
        defaults = preset.GetDefaults()

        if defaults:
            for default_key, default_value in defaults.items():
                if not self.GetConfigurations().HasConfigKey(default_key):
                    self.GetConfigurations().UpdateConfigValue(default_key, default_value)

    def GetConfigurations(self) -> SingleConfiguration:
        """ Safe return single_configuration object """
        if self.configurations:
            return self.configurations
        else:
            raise Exception(f"Configuration not loaded for {self.NAME}")

    def GetFromConfigurations(self, key):
        """ Get value from confiugurations with key (if not present raise Exception)."""
        if self.GetConfigurations().HasConfigKey(key):
            return self.GetConfigurations().GetConfigValue(key)
        else:
            raise Exception("Can't find key " + key + " in configurations")

    def GetTrueOrFalseFromConfigurations(self, key) -> bool:
        """ Get boolean value from confiugurations with key (if not present raise Exception) """
        value = self.GetFromConfigurations(key).lower()
        if value in BooleanAnswers.TRUE_ANSWERS:
            return True
        else:
            return False

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        """ Prepare a preset to manage settings insert/edit for the warehouse or entity """
        return MenuPreset()
