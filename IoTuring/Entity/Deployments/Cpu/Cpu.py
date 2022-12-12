import psutil
from IoTuring.Entity.ValueFormatter import ValueFormatter
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
        self.SetEntitySensorValue(KEY_PERCENTAGE, psutil.cpu_percent(),
                                  ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE, 1))
        self.SetEntitySensorValue(KEY_COUNT, psutil.cpu_count())
        # CPU times
        self.SetEntitySensorValue(KEY_TIMES_USER, psutil.cpu_times()[
            0], ValueFormatter.Options(ValueFormatter.TYPE_MILLISECONDS))
        self.SetEntitySensorValue(KEY_TIMES_SYSTEM, psutil.cpu_times()[
            1], ValueFormatter.Options(ValueFormatter.TYPE_MILLISECONDS))
        self.SetEntitySensorValue(KEY_TIMES_IDLE, psutil.cpu_times()[
            2], ValueFormatter.Options(ValueFormatter.TYPE_MILLISECONDS))
        # CPU stats
        self.SetEntitySensorValue(KEY_STATS_CTX, psutil.cpu_stats(
        )[0], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
        self.SetEntitySensorValue(KEY_STATS_INTERR, psutil.cpu_stats()[
                                  1], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
        # CPU freq
        self.SetEntitySensorValue(KEY_FREQ_CURRENT, MHZ * psutil.cpu_freq()[
            0], ValueFormatter.Options(ValueFormatter.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz"))
        self.SetEntitySensorValue(KEY_FREQ_MIN, MHZ * psutil.cpu_freq()[
            1], ValueFormatter.Options(ValueFormatter.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz"))
        self.SetEntitySensorValue(KEY_FREQ_MAX, MHZ * psutil.cpu_freq()[
            2], ValueFormatter.Options(ValueFormatter.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz"))
        if self.os != 'macOS':
            # CPU avg load
            self.SetEntitySensorValue(KEY_AVERAGE_LOAD_LAST_1,
                                      psutil.getloadavg()[0], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
            self.SetEntitySensorValue(KEY_AVERAGE_LOAD_LAST_5,
                                      psutil.getloadavg()[1], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
            self.SetEntitySensorValue(KEY_AVERAGE_LOAD_LAST_15,
                                      psutil.getloadavg()[2], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
