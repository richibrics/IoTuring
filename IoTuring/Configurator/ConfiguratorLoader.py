from __future__ import annotations
from IoTuring.Entity.Entity import Entity
from IoTuring.Logger.LogObject import LogObject
from IoTuring.Configurator.Configurator import KEY_ENTITY_TYPE, Configurator, KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES, KEY_WAREHOUSE_TYPE
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager
from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.Warehouse.Warehouse import Warehouse


class ConfiguratorLoader(LogObject):
    configurator = None

    def __init__(self, configurator: Configurator) -> None:
        self.configurations = configurator.GetConfigurations()

    # Return list of instances initialized using their configurations
    def LoadWarehouses(self) -> list[Warehouse]:
        warehouses = []
        wcm = WarehouseClassManager()
        if not KEY_ACTIVE_WAREHOUSES in self.configurations:
            self.Log(
                self.LOG_ERROR, "You have to enable at least one warehouse: configure it using -c argument")
            exit(1)
        for activeWarehouse in self.configurations[KEY_ACTIVE_WAREHOUSES]:
            # Get WareHouse named like in config type field, then init it with configs and add it to warehouses list
            whClass = wcm.GetClassFromName(
                activeWarehouse[KEY_WAREHOUSE_TYPE]+"Warehouse")

            if whClass is None:
                self.Log(self.LOG_ERROR, "Can't find " +
                         activeWarehouse[KEY_WAREHOUSE_TYPE] + " warehouse, check your configurations.")
            else:
                whClass(activeWarehouse).AddMissingDefaultConfigs()
                warehouses.append(whClass(activeWarehouse))
        return warehouses

    # warehouses[0].AddEntity(eM.NewEntity(eM.EntityNameToClass("Username")).getInstance()): may be useful
    # Return list of entities initialized
    def LoadEntities(self) -> list[Entity]:
        entities = []
        ecm = EntityClassManager()
        if not KEY_ACTIVE_ENTITIES in self.configurations:
            self.Log(
                self.LOG_ERROR, "You have to enable at least one entity: configure it using -c argument")
            exit(1)
        for activeEntity in self.configurations[KEY_ACTIVE_ENTITIES]:
            entityClass = ecm.GetClassFromName(activeEntity[KEY_ENTITY_TYPE])
            if entityClass is None:
                self.Log(self.LOG_ERROR, "Can't find " +
                         activeEntity[KEY_ENTITY_TYPE] + " entity, check your configurations.")
            else:
                entityClass(activeEntity).AddMissingDefaultConfigs()
                entities.append(entityClass(activeEntity))  # Entity instance
        return entities

    # How Warehouse configurations works:
    # - in Main I have a Configurator()
    # - then I create a ConfiguratorLoader(), passing the Configurator()
    # - the CL reads the configuration for each active Warehouse
    # - for each one:
    #   - pass the configuration to the warehouse function that uses the configuration to init the Warehouse
    #   - append the Warehouse to the list
