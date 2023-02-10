import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions

# Sensor: Virtual memory
KEY_MEMORY_PERCENTAGE = 'physical_memory_percentage'
# Extra data keys
EXTRA_KEY_MEMORY_TOTAL = 'Physical memory: total [MB]'
EXTRA_KEY_MEMORY_USED = 'Physical memory: used [MB]'
EXTRA_KEY_MEMORY_FREE = 'Physical memory: free [MB]'
EXTRA_KEY_MEMORY_AVAILABLE = 'Physical memory: available [MB]'

# Sensor: Swap memory
KEY_SWAP_PERCENTAGE = 'swap_memory_percentage'
# Extra data keys
EXTRA_KEY_SWAP_TOTAL = 'Swap memory: total [MB]'
EXTRA_KEY_SWAP_USED = 'Swap memory: used [MB]'
EXTRA_KEY_SWAP_FREE = 'Swap memory: free [MB]'


class Ram(Entity):
    NAME = "Ram"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_PERCENTAGE, True))
        self.RegisterEntitySensor(EntitySensor(self, KEY_SWAP_PERCENTAGE, True))

    def Update(self):
        # Virtual memory
        extra_physical_memory = {}
        self.SetEntitySensorValue(KEY_MEMORY_PERCENTAGE, psutil.virtual_memory()[
            2], ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE))

        # Extra
        extra_physical_memory[EXTRA_KEY_MEMORY_TOTAL] = ValueFormatter.GetFormattedValue(psutil.virtual_memory()[0], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        extra_physical_memory[EXTRA_KEY_MEMORY_USED]  = ValueFormatter.GetFormattedValue(psutil.virtual_memory()[3], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        extra_physical_memory[EXTRA_KEY_MEMORY_AVAILABLE]  = ValueFormatter.GetFormattedValue(psutil.virtual_memory()[1], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        extra_physical_memory[EXTRA_KEY_MEMORY_FREE]  = ValueFormatter.GetFormattedValue(psutil.virtual_memory()[4], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorExtraAttributes(KEY_MEMORY_PERCENTAGE, extra_physical_memory)
        
        # Swap memory
        extra_swap_memory = {}
        self.SetEntitySensorValue(KEY_SWAP_PERCENTAGE, psutil.swap_memory()[
            3], ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE))
        
        # Extra
        extra_swap_memory[EXTRA_KEY_SWAP_TOTAL] = ValueFormatter.GetFormattedValue(psutil.swap_memory()[0], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        extra_swap_memory[EXTRA_KEY_SWAP_USED]  = ValueFormatter.GetFormattedValue(psutil.swap_memory()[1], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        extra_swap_memory[EXTRA_KEY_SWAP_FREE]  = ValueFormatter.GetFormattedValue(psutil.swap_memory()[2], ValueFormatter.Options(ValueFormatter.TYPE_BYTE, 0, "MB"))
        self.SetEntitySensorExtraAttributes(KEY_SWAP_PERCENTAGE, extra_swap_memory)
