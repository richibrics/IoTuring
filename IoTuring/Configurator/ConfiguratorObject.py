from IoTuring.Configurator.MenuPreset import BooleanAnswers, MenuPreset
from IoTuring.Configurator.Configuration import SingleConfiguration


class ConfiguratorObject:
    """ Base class for configurable classes """

    def __init__(self, single_configuration: SingleConfiguration) -> None:
        self.configurations = single_configuration

    def GetConfigurations(self) -> dict:
        """ Return configuration as dict """
        return self.configurations.ToDict()

    def GetFromConfigurations(self, key):
        """ Get value from confiugurations with key (if not present raise Exception)."""
        if self.configurations.HasConfigKey(key):
            return self.configurations.GetConfigValue(key)
        else:
            raise Exception("Can't find key " + key + " in configurations")
        
    def GetTrueOrFalseFromConfigurations(self, key) -> bool:
        """ Get boolean value from confiugurations with key (if not present raise Exception) """
        value = self.GetFromConfigurations(key).lower()
        if value in BooleanAnswers.TRUE_ANSWERS:
            return True
        else:
            return False

    def AddMissingDefaultConfigs(self) -> None:
        """ If some default values are missing add them to the running configuration"""
        preset = self.ConfigurationPreset()
        defaults = preset.GetDefaults()

        if defaults:
            for default_key, default_value in defaults.items():
                if not self.configurations.HasConfigKey(default_key):
                    self.configurations.UpdateConfigValue(default_key, default_value)


    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        """ Prepare a preset to manage settings insert/edit for the warehouse or entity """
        return MenuPreset()
