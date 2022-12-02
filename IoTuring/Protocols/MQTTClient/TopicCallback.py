from IoTuring.Logger.LogObject import LogObject

import paho.mqtt.client as mqtt


class TopicCallback(LogObject):

    def __init__(self, topic, callback) -> None:
        super().__init__()
        if topic is None or callback is None:
            self.Log(self.LOG_ERROR, "Topic/Callback can't be null\nTopic: " +
                     topic + "\nCallback: " + callback)
            return
        self.topic = topic
        self.callback = callback
        self.imSubscribed = False

    def CompareTopic(self, wantedTopic):
        """ Return true if the passed topic equals to my topic """
        return self.topic == wantedTopic  # TODO Wildcard check maybe

    def Call_Callback(self, message):
        """ Call callback, need also the topic because may be used a wildcard in self.topic, so I want the complete topic ALWAYS """
        try:
            self.callback(message)
        except Exception as e:
            self.Log(self.LOG_ERROR, "Error in callback call\n --> Topic: " + message.topic +
                     "\n --> Payload: " + str(message.payload) + "\nError: " + str(e))

    def SetAsSubscribed(self):
        """ Set subscribed status to False """
        self.imSubscribed = True

    def SetAsNotSubscribed(self):
        """ Reset subscribed status to False """
        self.imSubscribed = False

    def GetSubscriptionState(self):
        """ Return True if I'm subscribed currently """
        return self.imSubscribed

    def SubscribeTopic(self, mqttClient: mqtt.Client):
        """ Subscribe to the topic using the passed MQTT client (if not already subscribed to) """
        if not self.GetSubscriptionState():
            mqttClient.subscribe(self.topic, 0)  # TODO QoS settings
            self.SetAsSubscribed()

    def UnsubscribeTopic(self, mqttClient: mqtt.Client):
        """ Unubscribe from the topic using the passed MQTT client """
        mqttClient.unsubscribe(self.topic)
        self.SetAsNotSubscribed()
