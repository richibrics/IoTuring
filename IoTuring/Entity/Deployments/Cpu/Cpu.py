import psutil
from IoTuring.Entity.ValueFormatter import ValueFormatter
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

FREQUENCY_DECIMALS = 0

MHZ = 1000000

# Sensor: CPU
KEY_PERCENTAGE = 'used_percentage'
# Extra data keys
EXTRA_KEY_COUNT = 'CPU Count'
# CPU times
EXTRA_KEY_TIMES_USER = 'User CPU time'
EXTRA_KEY_TIMES_SYSTEM = 'System CPU time'
EXTRA_KEY_TIMES_IDLE = 'Idle CPU time'
# CPU stats
EXTRA_KEY_STATS_CTX = 'Context switches since boot'
EXTRA_KEY_STATS_INTERR = 'Number of interrupts since boot'
# CPU avg load
EXTRA_KEY_AVERAGE_LOAD_LAST_1 = 'Average load last minute'
EXTRA_KEY_AVERAGE_LOAD_LAST_5 = 'Average load last 5 minutes'
EXTRA_KEY_AVERAGE_LOAD_LAST_15 = 'Average load last 15 minutes'

# Sensor: CPU frequency
KEY_FREQ_CURRENT = 'current_frequency'
# Extra data keys
EXTRA_KEY_FREQ_MIN = 'Minimum CPU frequency'
EXTRA_KEY_FREQ_MAX = 'Maximum CPU frequency'


class Cpu(Entity):
    NAME = "Cpu"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_PERCENTAGE, True))
        self.RegisterEntitySensor(EntitySensor(self, KEY_FREQ_CURRENT, True))

    def Update(self):
        # CPU Percentage
        extra_cpu_data = {}
        self.SetEntitySensorValue(KEY_PERCENTAGE, psutil.cpu_percent(),
                                  ValueFormatter.Options(ValueFormatter.TYPE_PERCENTAGE, 1))
        # Extra data
        extra_cpu_data[EXTRA_KEY_COUNT] = psutil.cpu_count()
        # CPU times
        extra_cpu_data[EXTRA_KEY_TIMES_USER] = ValueFormatter.GetFormattedValue(psutil.cpu_times()[
            0], ValueFormatter.Options(ValueFormatter.TYPE_MILLISECONDS))
        extra_cpu_data[EXTRA_KEY_TIMES_SYSTEM] = ValueFormatter.GetFormattedValue(psutil.cpu_times()[
            1], ValueFormatter.Options(ValueFormatter.TYPE_MILLISECONDS))
        extra_cpu_data[EXTRA_KEY_TIMES_IDLE] = ValueFormatter.GetFormattedValue(psutil.cpu_times()[
            2], ValueFormatter.Options(ValueFormatter.TYPE_MILLISECONDS))
        # CPU stats
        extra_cpu_data[EXTRA_KEY_STATS_CTX] = ValueFormatter.GetFormattedValue(psutil.cpu_stats(
        )[0], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
        extra_cpu_data[EXTRA_KEY_STATS_INTERR] = ValueFormatter.GetFormattedValue(psutil.cpu_stats()[
            1], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))

        # CPU avg load
        extra_cpu_data[EXTRA_KEY_AVERAGE_LOAD_LAST_1] = ValueFormatter.GetFormattedValue(
            psutil.getloadavg()[0], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
        extra_cpu_data[EXTRA_KEY_AVERAGE_LOAD_LAST_5] = ValueFormatter.GetFormattedValue(
            psutil.getloadavg()[1], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))
        extra_cpu_data[EXTRA_KEY_AVERAGE_LOAD_LAST_15] = ValueFormatter.GetFormattedValue(
            psutil.getloadavg()[2], ValueFormatter.Options(ValueFormatter.TYPE_NONE, 2))

        self.SetEntitySensorExtraAttributes(KEY_PERCENTAGE, extra_cpu_data)

        # CPU freq
        extra_cpu_freq_data = {}
        self.SetEntitySensorValue(KEY_FREQ_CURRENT, MHZ * psutil.cpu_freq()[
            0], ValueFormatter.Options(ValueFormatter.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz"))
        extra_cpu_freq_data[EXTRA_KEY_FREQ_MIN] = ValueFormatter.GetFormattedValue(MHZ * psutil.cpu_freq()[
            1], ValueFormatter.Options(ValueFormatter.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz"))
        extra_cpu_freq_data[EXTRA_KEY_FREQ_MAX] = ValueFormatter.GetFormattedValue(MHZ * psutil.cpu_freq()[
            2], ValueFormatter.Options(ValueFormatter.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz"))

        self.SetEntitySensorExtraAttributes(
            KEY_FREQ_CURRENT, extra_cpu_freq_data)
