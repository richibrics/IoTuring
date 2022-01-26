from Logger.LogObject import LogObject
from Configurator.Configurator import Configurator, KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES, KEY_WAREHOUSE_TYPE
from ClassManager.WarehouseClassManager import WarehouseClassManager
from ClassManager.EntityClassManager import EntityClassManager


class ConfiguratorLoader(LogObject):
    configurator = None

    def __init__(self, configurator: Configurator) -> None:
        self.configurations = configurator.GetConfigurations()

    # Return list of instances initialized using their configurations
    def LoadWarehouses(self) -> list:
        warehouses = []
        wcm = WarehouseClassManager()
        for activeWarehouse in self.configurations[KEY_ACTIVE_WAREHOUSES]:
            # Get WareHouse named like in config type field, then init it with configs and add it to warehouses list
            warehouses.append(wcm.GetClassFromName(
                activeWarehouse[KEY_WAREHOUSE_TYPE]+"Warehouse").InstantiateWithConfiguration(activeWarehouse))
        return warehouses

    # warehouses[0].AddEntity(eM.NewEntity(eM.EntityNameToClass("Username")).getInstance()): may be useful
    def LoadEntities(self) -> list:  # Return list of entities initialized
        entities = []
        ecm = EntityClassManager()
        for activeEntity in self.configurations[KEY_ACTIVE_ENTITIES]:
            entityClass = ecm.GetClassFromName(activeEntity)
            if entityClass is None:
                self.Log(self.LOG_ERROR, "Can't find " +
                         activeEntity + " entity, check your configurations.")
            else:
                entities.append(entityClass())
        return entities
