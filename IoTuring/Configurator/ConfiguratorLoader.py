from __future__ import annotations
from IoTuring.Entity.Entity import Entity
from IoTuring.Logger.LogObject import LogObject
from IoTuring.Configurator.Configurator import Configurator, KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager
from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.Warehouse.Warehouse import Warehouse


class ConfiguratorLoader(LogObject):
    configurator = None

    def __init__(self, configurator: Configurator) -> None:
        self.configurations = configurator.config

    # Return list of instances initialized using their configurations
    def LoadWarehouses(self) -> list[Warehouse]:
        warehouses = []
        wcm = WarehouseClassManager()
        if not self.configurations.GetConfigsInCategory(KEY_ACTIVE_WAREHOUSES):
            self.Log(
                self.LOG_ERROR, "You have to enable at least one warehouse: configure it using -c argument")
            exit(1)
        for whConfig in self.configurations.GetConfigsInCategory(KEY_ACTIVE_WAREHOUSES):
            # Get WareHouse named like in config type field, then init it with configs and add it to warehouses list
            whClass = wcm.GetClassFromName(whConfig.GetLongName())

            if whClass is None:
                self.Log(self.LOG_ERROR, f"Can't find {whConfig.GetType()} warehouse, check your configurations.")
            else:
                wh = whClass(whConfig)
                wh.AddMissingDefaultConfigs()
                self.Log(self.LOG_DEBUG, f"Full configuration with defaults: {wh.configurations}")
                warehouses.append(wh)
        return warehouses

    # warehouses[0].AddEntity(eM.NewEntity(eM.EntityNameToClass("Username")).getInstance()): may be useful
    # Return list of entities initialized
    def LoadEntities(self) -> list[Entity]:
        entities = []
        ecm = EntityClassManager()
        if not self.configurations.GetConfigsInCategory(KEY_ACTIVE_ENTITIES):
            self.Log(
                self.LOG_ERROR, "You have to enable at least one entity: configure it using -c argument")
            exit(1)
        for entityConfig in self.configurations.GetConfigsInCategory(KEY_ACTIVE_ENTITIES):
            entityClass = ecm.GetClassFromName(entityConfig.GetType())
            if entityClass is None:
                self.Log(self.LOG_ERROR, f"Can't find {entityConfig.GetType()} entity, check your configurations.")
            else:
                ec = entityClass(entityConfig)
                ec.AddMissingDefaultConfigs()
                self.Log(self.LOG_DEBUG, f"Full configuration with defaults: {ec.configurations}")
                entities.append(ec)  # Entity instance
        return entities

    # How Warehouse configurations works:
    # - in Main I have a Configurator()
    # - then I create a ConfiguratorLoader(), passing the Configurator()
    # - the CL reads the configuration for each active Warehouse
    # - for each one:
    #   - pass the configuration to the warehouse function that uses the configuration to init the Warehouse
    #   - append the Warehouse to the list
