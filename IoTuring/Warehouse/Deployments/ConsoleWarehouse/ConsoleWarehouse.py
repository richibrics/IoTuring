from IoTuring.Logger.Logger import Logger
from IoTuring.Warehouse.Warehouse import Warehouse


class ConsoleWarehouse(Warehouse):
    NAME = "Console"

    def Loop(self):
        for entity in self.GetEntities():
            for entitySensor in entity.GetEntitySensors():
                if entitySensor.HasValue():
                    self.Log(Logger.LOG_MESSAGE, 
                        f"{entitySensor.GetId()}: {entitySensor.GetValue()}")
            for entityCommand in entity.GetEntityCommands():
                if entityCommand.HasState():
                    self.Log(Logger.LOG_MESSAGE, 
                        f"{entityCommand.GetId()}: {entityCommand.GetState()}")
                    
