from Logger.Logger import Logger
from Warehouse.Warehouse import Warehouse

class ConsoleWarehouse(Warehouse):
    name = "Console"

    def Loop(self) -> None:
        for entity in self.GetEntities():
            for key in entity.KeyList():
                self.Log(Logger.LOG_MESSAGE,"Value for " + entity.GetGlobalKey(key) + ": " + entity.GetValue(key))    

    