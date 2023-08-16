import psutil
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
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

VALUEFORMATOPTIONS_CPU_PERCENTAGE = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_PERCENTAGE, 1)
VALUEFORMATOPTIONS_CPU_TIME = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_MILLISECONDS)
VALUEFORMATOPTIONS_ROUND2 = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_NONE, 2)
VALUEFORMATOPTIONS_CPU_FREQUENCY_MHZ = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_FREQUENCY, FREQUENCY_DECIMALS, "MHz")


class Cpu(Entity):
    NAME = "Cpu"

    def Initialize(self):
        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_PERCENTAGE,
                valueFormatterOptions=VALUEFORMATOPTIONS_CPU_PERCENTAGE,
                supportsExtraAttributes=True))
        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_FREQ_CURRENT,
                valueFormatterOptions=VALUEFORMATOPTIONS_CPU_FREQUENCY_MHZ,
                supportsExtraAttributes=True))

    def Update(self):
        # CPU Percentage
        self.SetEntitySensorValue(KEY_PERCENTAGE, psutil.cpu_percent())
        # Extra data
        self.SetEntitySensorExtraAttribute(
            KEY_PERCENTAGE, EXTRA_KEY_COUNT, psutil.cpu_count())
        # CPU times
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_TIMES_USER, psutil.cpu_times()[
            0], valueFormatterOptions=VALUEFORMATOPTIONS_CPU_TIME)
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_TIMES_SYSTEM, psutil.cpu_times()[
            1], valueFormatterOptions=VALUEFORMATOPTIONS_CPU_TIME)
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_TIMES_IDLE, psutil.cpu_times()[
            2], valueFormatterOptions=VALUEFORMATOPTIONS_CPU_TIME)
        # CPU stats
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_STATS_CTX, psutil.cpu_stats(
        )[0], valueFormatterOptions=VALUEFORMATOPTIONS_ROUND2)
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_STATS_INTERR, psutil.cpu_stats()[
            1], valueFormatterOptions=VALUEFORMATOPTIONS_ROUND2)

        # CPU avg load
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_AVERAGE_LOAD_LAST_1,
                                           psutil.getloadavg()[0], valueFormatterOptions=VALUEFORMATOPTIONS_ROUND2)
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_AVERAGE_LOAD_LAST_5,
                                           psutil.getloadavg()[1], valueFormatterOptions=VALUEFORMATOPTIONS_ROUND2)
        self.SetEntitySensorExtraAttribute(KEY_PERCENTAGE, EXTRA_KEY_AVERAGE_LOAD_LAST_15,
                                           psutil.getloadavg()[2], valueFormatterOptions=VALUEFORMATOPTIONS_ROUND2)

        # CPU freq
        self.SetEntitySensorValue(
            KEY_FREQ_CURRENT,
            value=MHZ * psutil.cpu_freq()[0])
        # Extra data
        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_FREQ_CURRENT,
            attributeKey=EXTRA_KEY_FREQ_MIN,
            attributeValue=MHZ * psutil.cpu_freq()[1],
            valueFormatterOptions=VALUEFORMATOPTIONS_CPU_FREQUENCY_MHZ)
        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_FREQ_CURRENT,
            attributeKey=EXTRA_KEY_FREQ_MAX,
            attributeValue=MHZ * psutil.cpu_freq()[2],
            valueFormatterOptions=VALUEFORMATOPTIONS_CPU_FREQUENCY_MHZ)
