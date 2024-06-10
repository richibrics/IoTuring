from __future__ import annotations

from IoTuring.ClassManager.consts import KEY_ENTITY, KEY_WAREHOUSE, KEY_SETTINGS
from IoTuring.Exceptions.Exceptions import UnknownConfigKeyException

CONFIG_CLASS = {
    KEY_ENTITY: "active_entities",
    KEY_WAREHOUSE: "active_warehouses",
    KEY_SETTINGS: "settings"
}

BLANK_CONFIGURATION = {
    CONFIG_CLASS[KEY_ENTITY]: [{"type": "AppInfo"}]
}


CONFIG_KEY_TAG = "tag"
CONFIG_KEY_TYPE = "type"


class SingleConfiguration:
    """Single configuration of an entity or warehouse"""

    def __init__(self, config_class: str, config_dict: dict) -> None:
        """Create a new SingleConfiguration

        Args:
            config_class (str): CONFIG_CLASS of the config
            config_dict (dict): All options as in config file
        """
        self.config_class = config_class
        self.config_type = config_dict.pop(CONFIG_KEY_TYPE)
        self.configurations = config_dict

    def GetType(self) -> str:
        """Get the type name of entity or warehouse (e.g. Cpu, Battery, HomeAssistant)"""
        return self.config_type

    def GetTag(self) -> str:
        """Get the tag of entity"""
        if CONFIG_KEY_TAG in self.configurations:
            return self.configurations[CONFIG_KEY_TAG]
        else:
            return ""

    def GetLabel(self) -> str:
        """Get the type name of this configuration, add tag if multi"""

        label = self.GetType()

        if self.GetTag():
            label += f" with tag {self.GetTag()}"

        return label

    def GetLongName(self) -> str:
        """ Get the type with the category name at the end (e.g. CpuEntity, HomeAssistantWarehouse)"""
        
        # Add category name to the end 
        return str(self.GetType() + self.GetClassKey().capitalize())

    def GetClassKey(self) -> str:
        """Get the CLASS_KEY of this configuration, e.g. KEY_ENTITY, KEY_WAREHOUSE"""
        return [i for i in CONFIG_CLASS if CONFIG_CLASS[i] == self.config_class][0]

    def GetConfigValue(self, config_key: str):
        """Get the value of a config key

        Args:
            config_key (str): The key of the configuration

        Raises:
            UnknownConfigKeyException: If the key is not found

        Returns:
            The value of the key.
        """
        if config_key in self.configurations:
            return self.configurations[config_key]
        else:
            raise UnknownConfigKeyException(config_key)

    def UpdateConfigValue(self, config_key: str, config_value: str) -> None:
        """Update the value of the configuration. Overwrites existing value

        Args:
            config_key (str): The key of the configuration
            config_value (str): The preferred value
        """
        self.configurations[config_key] = config_value

    def HasConfigKey(self, config_key: str) -> bool:
        """Check if key has a value

        Args:
            config_key (str): The key of the configuration

        Returns:
            bool: If it has a value
        """
        return bool(config_key in self.configurations)

    def ToDict(self, include_type: bool = True) -> dict:
        """ SingleConfiguration as a dict, as it would be saved to a file """
        full_dict = self.configurations
        if include_type:
            full_dict[CONFIG_KEY_TYPE] = self.GetType()
        return full_dict


class FullConfiguration:
    """Full configuration of all classes"""

    def __init__(self, config_dict: dict | None) -> None:
        """Initialize from dict or create blank

        Args:
            config_dict (dict | None): The config as dict or None to create blank
        """

        config_dict = config_dict or BLANK_CONFIGURATION
        self.configs = []

        for config_class, single_configs in config_dict.items():
            for single_config_dict in single_configs:

                self.configs.append(SingleConfiguration(
                    config_class, single_config_dict))

    def GetConfigsOfClass(self, class_key: str) -> list[SingleConfiguration]:
        """Return all configurations of class

        Args:
            class_key (str): CLASS_KEY of the class: e.g. KEY_ENTITY, KEY_WAREHOUSE

        Returns:
            list: Configurations in the class. Empty list if none found.
        """
        return [config for config in self.configs if config.config_class == CONFIG_CLASS[class_key]]

    def GetConfigsOfType(self, config_type: str) -> list[SingleConfiguration]:
        """Return all configs with the given type.

        For example all configurations of Notify entity.

        Args:
            config_type (str): The type of config to return

        Returns:
            list: Configurations of the given type. Empty list if none found.
        """

        return [config for config in self.configs if config.GetType() == config_type]

    def RemoveActiveConfiguration(self, config: SingleConfiguration) -> None:
        """Remove a configuration from the list of active configurations"""
        if config in self.configs:
            self.configs.remove(config)
        else:
            raise ValueError("Configuration not found")

    def AddConfiguration(self, class_key: str, config_type: str, single_config_dict: dict) -> None:
        """Add a new configuration to the list of active configurations

        Args:
            class_key (str): CLASS_KEY of the class: e.g. KEY_ENTITY, KEY_WAREHOUSE
            config_type (str): The type of the configuration
            single_config_dict (dict): all settings as a dict
        """

        config_class = CONFIG_CLASS[class_key]
        single_config_dict[CONFIG_KEY_TYPE] = config_type

        self.configs.append(SingleConfiguration(
            config_class, single_config_dict))

    def ToDict(self) -> dict:
        """Full configuration as a dict, for saving to file """
        config_dict = {}
        for class_key in CONFIG_CLASS:

            config_dict[CONFIG_CLASS[class_key]] = []

            for single_config in self.GetConfigsOfClass(class_key):
                config_dict[CONFIG_CLASS[class_key]].append(
                    single_config.ToDict())

        return config_dict
