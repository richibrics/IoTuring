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
                    self.Log(self.LOG_INFO, entitySensor.GetId() +
                             ": " + self.FormatValue(entitySensor))

    def FormatValue(self, entitySensor: EntitySensor):
        return ValueFormatter.FormatValue(entitySensor.GetValue(), entitySensor.GetValueFormatterOptions(), True)