import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormatter import ValueFormatter

# Virtual memory
KEY_MEMORY_TOTAL = 'physical_memory_total'
KEY_MEMORY_AVAILABLE = 'physical_memory_available'
KEY_MEMORY_FREE = 'physical_memory_free'
KEY_MEMORY_USED = 'physical_memory_used'
KEY_MEMORY_PERCENTAGE = 'physical_memory_percentage'
# Swap memory
KEY_SWAP_TOTAL = 'swap_memory_total'
KEY_SWAP_USED = 'swap_memory_used'
KEY_SWAP_FREE = 'swap_memory_free'
KEY_SWAP_PERCENTAGE = 'swap_memory_percentage'


class Ram(Entity):
    NAME = "Ram"

    def Initialize(self):

        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_PERCENTAGE))
        self.RegisterEntitySensor(EntitySensor(self, KEY_SWAP_PERCENTAGE))

        # Virtual memory
        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_TOTAL))
        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_AVAILABLE))
        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_FREE))
        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_USED))
        # Swap memory
        self.RegisterEntitySensor(EntitySensor(self, KEY_SWAP_TOTAL))
        self.RegisterEntitySensor(EntitySensor(self, KEY_SWAP_USED))
        self.RegisterEntitySensor(EntitySensor(self, KEY_SWAP_FREE))

    def Update(self):

        self.SetEntitySensorValue(KEY_MEMORY_PERCENTAGE, psutil.virtual_memory()[
            2], ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE))
        self.SetEntitySensorValue(KEY_SWAP_PERCENTAGE, psutil.swap_memory()[
            3], ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE))

        # Virtual memory
        self.SetEntitySensorValue(KEY_MEMORY_TOTAL,
                                  psutil.virtual_memory()[0], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorValue(KEY_MEMORY_AVAILABLE,
                                  psutil.virtual_memory()[1], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorValue(KEY_MEMORY_USED,
                                  psutil.virtual_memory()[3], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorValue(KEY_MEMORY_FREE,
                                  psutil.virtual_memory()[4], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        # Swap memory
        self.SetEntitySensorValue(
            KEY_SWAP_TOTAL, psutil.swap_memory()[0], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorValue(
            KEY_SWAP_USED,  psutil.swap_memory()[1], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorValue(
            KEY_SWAP_FREE, psutil.swap_memory()[2], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
