from __future__ import annotations

# config categories:
KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"
KEY_SETTINGS = "settings"

CONFIG_CATEGORY_NAME = {
    KEY_ACTIVE_ENTITIES: "Entity",
    KEY_ACTIVE_WAREHOUSES: "Warehouse",
    KEY_SETTINGS: "Setting"
}


BLANK_CONFIGURATION = {
    KEY_ACTIVE_ENTITIES: [{"type": "AppInfo"}],
    KEY_ACTIVE_WAREHOUSES: [],
    KEY_SETTINGS: []
}

KEY_ENTITY_TAG = "tag"
KEY_ENTITY_TYPE = "type"


class FullConfiguration:
    """Full configuration of all classes"""

    def __init__(self, config_dict: dict = BLANK_CONFIGURATION) -> None:

        self.configs = []

        for config_category in config_dict:
            for single_config_dict in config_dict[config_category]:
                self.configs.append(SingleConfiguration(
                    config_category, single_config_dict))

    def GetConfigsInCategory(self, config_category: str) -> list["SingleConfiguration"]:
        """Return all configurations in a category

        Args:
            config_category (str): KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES or KEY_SETTINGS

        Returns:
            list: Configurations in the category. Empty list if none found.
        """
        return [config for config in self.configs if config.config_category == config_category]

    def GetAllConfigsOfType(self, config_type: str, config_category: str = "") -> list["SingleConfiguration"]:
        """Return all configs with the given type, from the given category

        Args:
            config_type (str): The type of config to return
            config_category (str, optional): Optional filter for the category. Defaults to no filter.

        Returns:
            list: Configurations of the given type. Empty list if none found.
        """
        if config_category:
            config_list = self.GetConfigsInCategory(config_category)
        else:
            config_list = self.configs

        return [config for config in config_list if config.GetType() == config_type]

    def GetSingleConfigOfType(self, config_type: str) -> None | SingleConfiguration:
        """Return the only configuration of the given type. Raises exception if multiple found.

        Args:
            config_type (str): The type of config to return

        Raises:
            Exception: Multiple config found

        Returns:
            None | SingleConfiguration: The config, None if not found
        """
        configs = self.GetAllConfigsOfType(config_type=config_type)
        if not configs:
            return None
        if len(configs) > 1:
            raise Exception("Multiple configs found!")

        return configs[0]

    def RemoveActiveConfiguration(self, config: "SingleConfiguration") -> None:
        """Remove a configuration from the list of active configurations"""
        if config in self.configs:
            self.configs.remove(config)
        else:
            raise ValueError("Configuration not found")

    def AddConfiguration(self, config_category: str, single_config_dict: dict, config_type: str = "") -> "SingleConfiguration":
        """Add a new configuration to the list of active configurations

        Args:
            config_category (str): KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES or KEY_SETTINGS
            single_config_dict (dict): all settings as a dict
            config_type (str, optional): The type of the configuration, if not included in the dict.

        Raises:
            ValueError: Config type not defined in the dict nor in the function call

        Returns:
            SingleConfiguration: The new single config
        """

        if KEY_ENTITY_TYPE not in single_config_dict:
            if config_type:
                single_config_dict[KEY_ENTITY_TYPE] = config_type
            else:
                raise ValueError("Configuration type not specified")

        single_config = SingleConfiguration(
            config_category, single_config_dict)

        self.configs.append(single_config)

        return single_config

    def ToDict(self) -> dict:
        """Full configuration as a dict, for saving to file """
        config_dict = {}
        for config_category in BLANK_CONFIGURATION:
            config_dict[config_category] = []
            for single_config in self.GetConfigsInCategory(config_category):
                config_dict[config_category].append(single_config.ToDict())

        return config_dict


class SingleConfiguration:
    """Single configuraiton of an entity or warehouse or AppSettings"""

    config_category: str
    type: str
    configurations: dict

    def __init__(self, config_category: str, config_dict: dict) -> None:
        """Create a new SingleConfiguration

        Args:
            config_category (str): KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES or KEY_SETTINGS
            config_dict (dict): All options as in config file
        """
        self.config_category = config_category

        # self.type:
        setattr(self, KEY_ENTITY_TYPE, config_dict.pop(KEY_ENTITY_TYPE))

        self.configurations = config_dict

    def GetType(self) -> str:
        """ Get the type name of entity"""
        return getattr(self, KEY_ENTITY_TYPE)

    def GetTag(self) -> str:
        """ Get the tag of entity"""
        if KEY_ENTITY_TAG in self.configurations:
            return self.configurations[KEY_ENTITY_TAG]
        else:
            return ""

    def GetLabel(self) -> str:
        """ Get the type name of this configuration, add tag if multi"""

        label = self.GetType()

        if self.GetTag():
            label += f" with tag {self.GetTag()}"

        return label

    def GetLongName(self) -> str:
        """ Add category name to the end """
        return str(self.GetType() + self.GetCategoryName())

    def GetCategoryName(self) -> str:
        """ Get human readable singular name of the category of this configuration"""
        return CONFIG_CATEGORY_NAME[self.config_category]

    def GetConfigValue(self, config_key: str):
        """Get the value of a config key

        Args:
            config_key (str): The key of the configuration

        Raises:
            ValueError: If the key is not found

        Returns:
            The value of the key.
        """
        if config_key in self.configurations:
            return self.configurations[config_key]
        else:
            raise ValueError("Config key not set")

    def UpdateConfigValue(self, config_key: str, config_value: str) -> None:
        """Update the value of the configuration. Overwrites existing value

        Args:
            config_key (str): The key of the configuration
            config_value (str): The preferred value
        """
        self.configurations[config_key] = config_value

    def UpdateConfigDict(self, config_dict: dict) -> None:
        """Update all configurations with a dict. Overwrites existing values

        Args:
            config_dict (dict): The dict of configurations
        """
        self.configurations.update(config_dict)

    def HasConfigKey(self, config_key: str) -> bool:
        """Check if key has a value

        Args:
            config_key (str): The key of the configuration

        Returns:
            bool: If it has a value
        """
        return bool(config_key in self.configurations)

    def ToDict(self) -> dict:
        """Full configuration as a dict, as it would be saved to a file """
        full_dict = self.configurations
        full_dict[KEY_ENTITY_TYPE] = getattr(self, KEY_ENTITY_TYPE)
        return full_dict
