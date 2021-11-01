import datetime
from Entities.Entity import Entity


TOPIC_MESSAGE_TIME = 'message_time'


class Time(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC_MESSAGE_TIME)

    def Update(self):
        self.SetTopicValue(TOPIC_MESSAGE_TIME, self.GetCurrentTime())

    def GetCurrentTime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
