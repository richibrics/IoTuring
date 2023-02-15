import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions

# Sensor: Virtual memory
KEY_MEMORY_PERCENTAGE = 'physical_memory_percentage'
# Extra data keys
EXTRA_KEY_MEMORY_TOTAL = 'Physical memory: total'
EXTRA_KEY_MEMORY_USED = 'Physical memory: used'
EXTRA_KEY_MEMORY_FREE = 'Physical memory: free'
EXTRA_KEY_MEMORY_AVAILABLE = 'Physical memory: available'

# Sensor: Swap memory
KEY_SWAP_PERCENTAGE = 'swap_memory_percentage'
# Extra data keys
EXTRA_KEY_SWAP_TOTAL = 'Swap memory: total'
EXTRA_KEY_SWAP_USED = 'Swap memory: used'
EXTRA_KEY_SWAP_FREE = 'Swap memory: free'

VALUEFORMATOPTIONS_MEMORY_PERCENTAGE = ValueFormatterOptions(ValueFormatterOptions.TYPE_PERCENTAGE, 1)
VALUEFORMATOPTIONS_MEMORY_MB = ValueFormatterOptions(ValueFormatterOptions.TYPE_BYTE, 0, "MB")

class Ram(Entity):
    NAME = "Ram"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_MEMORY_PERCENTAGE, valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_PERCENTAGE, supportsExtraAttributes=True))
        self.RegisterEntitySensor(EntitySensor(self, KEY_SWAP_PERCENTAGE, valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_PERCENTAGE, supportsExtraAttributes=True))

    def Update(self):
        # Virtual memory
        self.SetEntitySensorValue(KEY_MEMORY_PERCENTAGE, psutil.virtual_memory()[2])

        # Extra
        self.SetEntitySensorExtraAttribute(KEY_MEMORY_PERCENTAGE, EXTRA_KEY_MEMORY_TOTAL, psutil.virtual_memory()[0], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
        self.SetEntitySensorExtraAttribute(KEY_MEMORY_PERCENTAGE, EXTRA_KEY_MEMORY_USED, psutil.virtual_memory()[3], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
        self.SetEntitySensorExtraAttribute(KEY_MEMORY_PERCENTAGE, EXTRA_KEY_MEMORY_AVAILABLE, psutil.virtual_memory()[1], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
        self.SetEntitySensorExtraAttribute(KEY_MEMORY_PERCENTAGE, EXTRA_KEY_MEMORY_FREE, psutil.virtual_memory()[4], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
        
        # Swap memory
        self.SetEntitySensorValue(KEY_SWAP_PERCENTAGE, psutil.swap_memory()[3])
        
        # Extra
        self.SetEntitySensorExtraAttribute(KEY_SWAP_PERCENTAGE, EXTRA_KEY_SWAP_TOTAL, psutil.swap_memory()[0], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
        self.SetEntitySensorExtraAttribute(KEY_SWAP_PERCENTAGE, EXTRA_KEY_SWAP_USED, psutil.swap_memory()[1], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
        self.SetEntitySensorExtraAttribute(KEY_SWAP_PERCENTAGE, EXTRA_KEY_SWAP_FREE, psutil.swap_memory()[2], valueFormatterOptions=VALUEFORMATOPTIONS_MEMORY_MB)
