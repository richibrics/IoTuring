from IoTuring.Configurator.MenuPreset import BooleanAnswers, MenuPreset
from IoTuring.Configurator.Configuration import SingleConfiguration, CONFIG_CLASS, CONFIG_KEY_TYPE
from IoTuring.Exceptions.Exceptions import UnknownConfigKeyException



class ConfiguratorObject:
    """ Base class for configurable classes """
    NAME = "Unnamed"
    ALLOW_MULTI_INSTANCE = False

    def __init__(self, single_configuration: SingleConfiguration) -> None:
        self.configurations = single_configuration

        # Add missing default values:
        defaults = self.ConfigurationPreset().GetDefaults()

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
            raise UnknownConfigKeyException(key)

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

    @classmethod
    def AllowMultiInstance(cls):
        """ Return True if this Entity can have multiple instances, useful for customizable entities 
            These entities are the ones that must have a tag to be recognized """
        return cls.ALLOW_MULTI_INSTANCE

    @classmethod
    def GetClassKey(cls) -> str:
        """Get the CLASS_KEY of this configuration, e.g. KEY_ENTITY, KEY_WAREHOUSE"""
        class_key = cls.__bases__[0].__name__.lower()
        if class_key not in CONFIG_CLASS:
            raise Exception(f"Invalid class {class_key}")
        return class_key

    @classmethod
    def GetDefaultConfigurations(cls) -> SingleConfiguration:
        """Get the default configuration of this class"""

        # Get default configs as dict:
        config_dict = cls.ConfigurationPreset().GetDefaults()
        config_dict[CONFIG_KEY_TYPE] = cls.NAME

        return SingleConfiguration(cls.GetClassKey(), config_dict=config_dict)
