from IoTuring.Logger.Logger import Logger
from IoTuring.Warehouse.Warehouse import Warehouse
from IoTuring.Entity.ValueFormat import ValueFormatter
from IoTuring.Entity.EntityData import EntitySensor

class ConsoleWarehouse(Warehouse):
    NAME = "Console"

    def Loop(self):
        for entity in self.GetEntities():
            for entitySensor in entity.GetEntitySensors():
                if(entitySensor.HasValue()):
                    self.Log(Logger.LOG_MESSAGE, entitySensor.GetId() +
                             ": " + self.FormatValue(entitySensor))

    def FormatValue(self, entitySensor: EntitySensor):
        return ValueFormatter.FormatValue(entitySensor.GetValue(), entitySensor.GetValueFormatterOptions(), True)