import psutil
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

FREQUENCY_DECIMALS = 0

MHZ = 1000000

# Basic CPU info
KEY_PERCENTAGE = 'cpu_used_percentage'
KEY_COUNT = 'cpu_count'
# Advanced CPU info
# CPU times
KEY_TIMES_USER = 'cpu_times_user'
KEY_TIMES_SYSTEM = 'cpu_times_system'
KEY_TIMES_IDLE = 'cpu_times_idle'
# CPU stats
KEY_STATS_CTX = 'cpu_stats_ctx_switches'
KEY_STATS_INTERR = 'cpu_stats_interrupts'
# CPU freq
KEY_FREQ_MIN = 'cpu_freq_min'
KEY_FREQ_MAX = 'cpu_freq_max'
KEY_FREQ_CURRENT = 'cpu_freq_current'
# CPU avg load
KEY_AVERAGE_LOAD_LAST_1 = 'cpu_avg_load_1minute'
KEY_AVERAGE_LOAD_LAST_5 = 'cpu_avg_load_5minutes'
KEY_AVERAGE_LOAD_LAST_15 = 'cpu_avg_load_15minutes'


class Cpu(Entity):
    NAME = "Cpu"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_PERCENTAGE))
        self.RegisterEntitySensor(EntitySensor(self, KEY_COUNT))

        # CPU times
        self.RegisterEntitySensor(EntitySensor(self, KEY_TIMES_USER))
        self.RegisterEntitySensor(EntitySensor(self, KEY_TIMES_SYSTEM))
        self.RegisterEntitySensor(EntitySensor(self, KEY_TIMES_IDLE))
        # CPU stats
        self.RegisterEntitySensor(EntitySensor(self, KEY_STATS_CTX))
        self.RegisterEntitySensor(EntitySensor(self, KEY_STATS_INTERR))
        # CPU freq
        self.RegisterEntitySensor(EntitySensor(self, KEY_FREQ_MIN))
        self.RegisterEntitySensor(EntitySensor(self, KEY_FREQ_MAX))
        self.RegisterEntitySensor(EntitySensor(self, KEY_FREQ_CURRENT))

    def PostInitialize(self):
        self.os = self.GetDependentEntitySensorValue('Os', "operating_system")
        if self.os != 'macOS':
            # CPU avg load (not available in macos)
            self.RegisterEntitySensor(
                EntitySensor(self, KEY_AVERAGE_LOAD_LAST_1))
            self.RegisterEntitySensor(
                EntitySensor(self, KEY_AVERAGE_LOAD_LAST_5))
            self.RegisterEntitySensor(
                EntitySensor(self, KEY_AVERAGE_LOAD_LAST_15))

    def Update(self):
        pass