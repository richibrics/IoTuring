import psutil
from Entity.Entity import Entity 


# Basic CPU info
TOPIC_PERCENTAGE = 'cpu/cpu_used_percentage'
TOPIC_COUNT = 'cpu/cpu_count'
# Advanced CPU info
# CPU times
TOPIC_TIMES_USER = 'cpu/cpu_times/user'
TOPIC_TIMES_SYSTEM = 'cpu/cpu_times/system'
TOPIC_TIMES_IDLE = 'cpu/cpu_times/idle'
# CPU stats
TOPIC_STATS_CTX = 'cpu/cpu_stats/ctx_switches'
TOPIC_STATS_INTERR = 'cpu/cpu_stats/interrupts'
# CPU freq
TOPIC_FREQ_MIN = 'cpu/cpu_freq/min'
TOPIC_FREQ_MAX = 'cpu/cpu_freq/max'
TOPIC_FREQ_CURRENT = 'cpu/cpu_freq/current'
# CPU avg load
TOPIC_AVERAGE_LOAD_LAST_1 = 'cpu/cpu_avg_load/1minute'
TOPIC_AVERAGE_LOAD_LAST_5 = 'cpu/cpu_avg_load/5minutes'
TOPIC_AVERAGE_LOAD_LAST_15 = 'cpu/cpu_avg_load/15minutes'

# Supports ADVANCED


class Cpu(Entity):
    def Initialize(self):

        self.AddTopic(TOPIC_PERCENTAGE)
        self.AddTopic(TOPIC_COUNT)

        # Advanced only if asked in options
        if self.GetOption(self.consts.ADVANCED_INFO_OPTION_KEY):
            # CPU times
            self.AddTopic(TOPIC_TIMES_USER)
            self.AddTopic(TOPIC_TIMES_SYSTEM)
            self.AddTopic(TOPIC_TIMES_IDLE)
            # CPU stats
            self.AddTopic(TOPIC_STATS_CTX)
            self.AddTopic(TOPIC_STATS_INTERR)
            # CPU freq
            self.AddTopic(TOPIC_FREQ_MIN)
            self.AddTopic(TOPIC_FREQ_MAX)
            self.AddTopic(TOPIC_FREQ_CURRENT)

    def PostInitialize(self):
        self.os = self.GetOS()
        if self.os != 'macOS' and self.GetOption(self.consts.ADVANCED_INFO_OPTION_KEY):
            # CPU avg load (not available in macos)
            self.AddTopic(TOPIC_AVERAGE_LOAD_LAST_1)
            self.AddTopic(TOPIC_AVERAGE_LOAD_LAST_5)
            self.AddTopic(TOPIC_AVERAGE_LOAD_LAST_15)

    def Update(self):
        # Send base data
        self.SetTopicValue(TOPIC_PERCENTAGE, psutil.cpu_percent(),
                           self.ValueFormatter.TYPE_PERCENTAGE)
        self.SetTopicValue(TOPIC_COUNT, psutil.cpu_count())
        # Send if wanted, extra data
        if self.GetOption(self.consts.ADVANCED_INFO_OPTION_KEY):
            # CPU times
            self.SetTopicValue(TOPIC_TIMES_USER, psutil.cpu_times()[
                               0], self.ValueFormatter.TYPE_TIME)
            self.SetTopicValue(TOPIC_TIMES_SYSTEM, psutil.cpu_times()[
                               1], self.ValueFormatter.TYPE_TIME)
            self.SetTopicValue(TOPIC_TIMES_IDLE, psutil.cpu_times()[
                               2], self.ValueFormatter.TYPE_TIME)
            # CPU stats
            self.SetTopicValue(TOPIC_STATS_CTX, psutil.cpu_stats()[0])
            self.SetTopicValue(TOPIC_STATS_INTERR, psutil.cpu_stats()[1])
            # CPU freq
            self.SetTopicValue(TOPIC_FREQ_CURRENT, psutil.cpu_freq()[
                               0], self.ValueFormatter.TYPE_FREQUENCY)
            self.SetTopicValue(TOPIC_FREQ_MIN, psutil.cpu_freq()[
                               1], self.ValueFormatter.TYPE_FREQUENCY)
            self.SetTopicValue(TOPIC_FREQ_MAX, psutil.cpu_freq()[
                               2], self.ValueFormatter.TYPE_FREQUENCY)
            if self.os != 'macOS':
                # CPU avg load
                self.SetTopicValue(TOPIC_AVERAGE_LOAD_LAST_1,
                                   psutil.getloadavg()[0])
                self.SetTopicValue(TOPIC_AVERAGE_LOAD_LAST_5,
                                   psutil.getloadavg()[1])
                self.SetTopicValue(TOPIC_AVERAGE_LOAD_LAST_15,
                                   psutil.getloadavg()[2])

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
