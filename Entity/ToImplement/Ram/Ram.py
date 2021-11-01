import psutil
import math
from Entities.Entity import Entity

# Virtual memory
TOPIC_MEMORY_TOTAL = 'ram/physical_memory/total'
TOPIC_MEMORY_AVAILABLE = 'ram/physical_memory/available'
TOPIC_MEMORY_FREE = 'ram/physical_memory/free'
TOPIC_MEMORY_USED = 'ram/physical_memory/used'
TOPIC_MEMORY_PERCENTAGE = 'ram/physical_memory/percentage'
# Swap memory
TOPIC_SWAP_TOTAL = 'ram/swap_memory/total'
TOPIC_SWAP_USED = 'ram/swap_memory/used'
TOPIC_SWAP_FREE = 'ram/swap_memory/free'
TOPIC_SWAP_PERCENTAGE = 'ram/swap_memory/percentage'

# Supports SIZED, ADVANCED


class Ram(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC_MEMORY_PERCENTAGE)
        self.AddTopic(TOPIC_SWAP_PERCENTAGE)

        if self.GetOption(self.consts.ADVANCED_INFO_OPTION_KEY):
            # Virtual memory
            self.AddTopic(TOPIC_MEMORY_TOTAL)
            self.AddTopic(TOPIC_MEMORY_AVAILABLE)
            self.AddTopic(TOPIC_MEMORY_FREE)
            self.AddTopic(TOPIC_MEMORY_USED)
            # Swap memory
            self.AddTopic(TOPIC_SWAP_TOTAL)
            self.AddTopic(TOPIC_SWAP_USED)
            self.AddTopic(TOPIC_SWAP_FREE)

    def Update(self):

        self.SetTopicValue(TOPIC_MEMORY_PERCENTAGE, psutil.virtual_memory()[
                           2], self.ValueFormatter.TYPE_PERCENTAGE)
        self.SetTopicValue(TOPIC_SWAP_PERCENTAGE, psutil.swap_memory()[
                           3], self.ValueFormatter.TYPE_PERCENTAGE)

        if self.GetOption(self.consts.ADVANCED_INFO_OPTION_KEY):
            # Virtual memory
            self.SetTopicValue(TOPIC_MEMORY_TOTAL,
                               psutil.virtual_memory()[0], self.ValueFormatter.TYPE_BYTE)
            self.SetTopicValue(TOPIC_MEMORY_AVAILABLE,
                               psutil.virtual_memory()[1], self.ValueFormatter.TYPE_BYTE)
            self.SetTopicValue(TOPIC_MEMORY_USED,
                               psutil.virtual_memory()[3], self.ValueFormatter.TYPE_BYTE)
            self.SetTopicValue(TOPIC_MEMORY_FREE,
                               psutil.virtual_memory()[4], self.ValueFormatter.TYPE_BYTE)
            # Swap memory
            self.SetTopicValue(
                TOPIC_SWAP_TOTAL, psutil.swap_memory()[0], self.ValueFormatter.TYPE_BYTE)
            self.SetTopicValue(
                TOPIC_SWAP_USED,  psutil.swap_memory()[1], self.ValueFormatter.TYPE_BYTE)
            self.SetTopicValue(
                TOPIC_SWAP_FREE, psutil.swap_memory()[2], self.ValueFormatter.TYPE_BYTE)
