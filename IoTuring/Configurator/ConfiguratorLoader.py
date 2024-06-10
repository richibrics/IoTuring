from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from IoTuring.Entity.Entity import Entity
    from IoTuring.Warehouse.Warehouse import Warehouse
    from IoTuring.Settings.Settings import Settings

import sys

from IoTuring.Logger.LogObject import LogObject
from IoTuring.Configurator.Configurator import Configurator
from IoTuring.ClassManager.ClassManager import ClassManager, KEY_ENTITY, KEY_WAREHOUSE, KEY_SETTINGS


class ConfiguratorLoader(LogObject):

    def __init__(self, configurator: Configurator) -> None:
        self.configurations = configurator.config

    # Return list of instances initialized using their configurations
    def LoadWarehouses(self) -> list[Warehouse]:
        warehouses = []
        wcm = ClassManager(KEY_WAREHOUSE)
        if not self.configurations.GetConfigsOfClass(KEY_WAREHOUSE):
            self.Log(
                self.LOG_ERROR, "You have to enable at least one warehouse: configure it using -c argument")
            sys.exit("No warehouse enabled")
        for whConfig in self.configurations.GetConfigsOfClass(KEY_WAREHOUSE):
            # Get WareHouse named like in config type field, then init it with configs and add it to warehouses list
            whClass = wcm.GetClassFromName(whConfig.GetLongName())

            if whClass is None:
                self.Log(
                    self.LOG_ERROR, f"Can't find {whConfig.GetType} warehouse, check your configurations.")
            else:
                wh = whClass(whConfig)
                self.Log(
                    self.LOG_DEBUG, f"Full configuration with defaults: {wh.configurations.ToDict()}")
                warehouses.append(wh)
        return warehouses

    # warehouses[0].AddEntity(eM.NewEntity(eM.EntityNameToClass("Username")).getInstance()): may be useful
    # Return list of entities initialized
    def LoadEntities(self) -> list[Entity]:
        entities = []
        ecm = ClassManager(KEY_ENTITY)
        if not self.configurations.GetConfigsOfClass(KEY_ENTITY):
            self.Log(
                self.LOG_ERROR, "You have to enable at least one entity: configure it using -c argument")
            sys.exit("No entity enabled")
        for entityConfig in self.configurations.GetConfigsOfClass(KEY_ENTITY):
            entityClass = ecm.GetClassFromName(entityConfig.GetType())
            if entityClass is None:
                self.Log(
                    self.LOG_ERROR, f"Can't find {entityConfig.GetType()} entity, check your configurations.")
            else:
                ec = entityClass(entityConfig)
                self.Log(
                    self.LOG_DEBUG, f"Full configuration with defaults: {ec.configurations.ToDict()}")
                entities.append(ec)  # Entity instance
        return entities

    # How Warehouse configurations works:
    # - in Main I have a Configurator()
    # - then I create a ConfiguratorLoader(), passing the Configurator()
    # - the CL reads the configuration for each active Warehouse
    # - for each one:
    #   - pass the configuration to the warehouse function that uses the configuration to init the Warehouse
    #   - append the Warehouse to the list

    def LoadSettings(self, early_init:bool = False) -> list[Settings]:
        """ Load all Settings classes

        Args:
            early_init (bool, optional): True when loaded before configurator menu, False when added to SettingsManager. Defaults to False.

        Returns:
            list[Settings]: Loaded classes
        """

        settings = []
        scm = ClassManager(KEY_SETTINGS)
        settingsClasses = scm.ListAvailableClasses()

        for sClass in settingsClasses:

            # Check if config was saved:
            savedConfigs = self.configurations\
                .GetConfigsOfType(sClass.NAME)

            if savedConfigs:
                sc = sClass(savedConfigs[0], early_init)

            # Fallback to default:
            else:
                sc = sClass(sClass.GetDefaultConfigurations(), early_init)

            settings.append(sc)
        return settings

    # How Settings configurations work:
    # - Settings' configs are added to SettingsManager singleton on main __init__
    # - For advanced usage custom loading could be set up in the class' __init()__
    # - Setting classes has classmethods to get their configs from SettingsManager Singleton,
    #   SettingsManager shouldn't be called directly, e.g: 
    #   AppSettings.GetFromSettingsConfigurations(CONFIG_KEY_UPDATE_INTERVAL)
