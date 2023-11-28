from IoTuring.Configurator.MenuPreset import BooleanAnswers
from IoTuring.Configurator.MenuPreset import MenuPreset


class ConfiguratorObject:
    """ Base class for configurable classes """

    def __init__(self, configurations) -> None:
        self.configurations = configurations

    def GetConfigurations(self) -> dict:
        """ Safe return configurations dict """
        return self.configurations.copy()

    def GetFromConfigurations(self, key):
        """ Get value from confiugurations with key (if not present raise Exception) """
        if key in self.GetConfigurations():
            return self.GetConfigurations()[key]
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
            for default_key in defaults:
                if default_key not in self.GetConfigurations():
                    self.configurations[default_key] = defaults[default_key]

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        """ Prepare a preset to manage settings insert/edit for the warehouse or entity """
        return MenuPreset()
