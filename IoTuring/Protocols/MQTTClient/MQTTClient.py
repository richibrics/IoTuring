from IoTuring.Logger.LogObject import LogObject
from IoTuring.MyApp.App import App
import paho.mqtt.client as MqttClient
import paho.mqtt.publish as publish

from IoTuring.Protocols.MQTTClient.TopicCallback import TopicCallback

"""

MQTTClient Operations:
- Init
- AsyncConnect
- SendTopicData
- AddNewTopicToSubscribeTo

"""


class MQTTClient(LogObject):
    client = None
    connected = False

    # After the init, you have to connect with AsyncConnect !
    def __init__(self, address, port=1883, name=None, username="", password=""):
        self.address = address
        self.port = int(port)
        self.name = name
        self.username = username
        self.password = password

        if self.name == None:
            self.name = App.getName()

        # List of TopicCallback objects, which I use to call callbacks, compare topics, keep subscribed state
        self.topicCallbacks = []

        self.Log(self.LOG_INFO, 'Preparing MQTT client')
        self.SetupClient()

    def IsConnected(self):
        """ Return True if client is currently connected """
        return self.connected

    def SetupClient(self) -> None:
        self.client = MqttClient.Client(self.name)

        if self.username != "" and self.password != "":
            self.client.username_pw_set(self.username, self.password)

        # Assign event callbacks
        self.client.on_connect = self.Event_OnClientConnect
        self.client.on_disconnect = self.Event_OnClientDisconnect
        self.client.on_message = self.Event_OnMessageReceive

    def AsyncConnect(self) -> None:
        """ Connect async to the broker """
        self.Log(self.LOG_INFO, 'MQTT Client ready to connect to the broker')
        # If broker is not reachable wait till he's reachable
        self.client.connect_async(self.address, port=self.port)
        self.client.loop_start()

    # EVENTS

    def Event_OnClientConnect(self, client, userdata, flags, rc) -> None:
        if rc == 0:  # Connections is OK
            self.Log(self.LOG_INFO, "Connection established")
            self.connected = True
            self.SubscribeToAllTopics()
        else:
            self.Log(self.LOG_ERROR, "Connection error")

    def Event_OnClientDisconnect(self, client, userdata, rc) -> None:
        self.Log(self.LOG_ERROR, "Connection lost")
        self.connected = False

        for topicCallback in self.topicCallbacks:
            topicCallback.SetAsNotSubscribed()

    def Event_OnMessageReceive(self, client, userdata, message) -> None:
        # TODO QoS also here
        try:
            topicCallback = self.GetTopicCallback(message.topic)
            topicCallback.Call_Callback(message)
        except Exception as e:
            self.Log(self.LOG_WARNING, "Error in message receive: " + str(e))

    # OUTCOMING MESSAGES PART

    def SendTopicData(self, topic, data) -> None:
        self.client.publish(topic, data)

    def LwtSet(self, topic, payload) -> None:
        # Sets Lwt message data
        self.client.will_set(topic, payload=payload, retain=False)

    # INCOMING MESSAGES PART / SUBSCRIBE

    def AddNewTopicToSubscribeTo(self, topic, callbackFunction) -> TopicCallback:
        topicCallback = TopicCallback(topic, callbackFunction)
        self.topicCallbacks.append(topicCallback)
        if self.connected:
            topicCallback.SubscribeTopic(self.client)
        return TopicCallback

    def SubscribeToAllTopics(self) -> None:
        """ Subscribe all TopicCallback using the MQTT client, if client is connected """
        if self.connected:
            for topicCallback in self.topicCallbacks:
                topicCallback.SubscribeTopic(self.client)

    def UnsubscribeFromTopic(self, topic) -> None:
        try:
            topicCallback = self.GetTopicCallback(topic)
            topicCallback.UnsubscribeTopic(self.client)
            self.topicCallbacks.remove(topicCallback)
        except Exception as e:
            self.Log(self.LOG_ERROR, "Error in topic unsubscription: " + str(e))

    def GetTopicCallbacks(self) -> list:
        """ Return (safely) a list with topics to which the client should be subscribed when everything is working correctly"""
        return self.topicCallbacks.copy()

    def GetTopicCallback(self, topic) -> TopicCallback:
        for topicCallback in self.topicCallbacks:
            if topicCallback.CompareTopic(topic):
                return topicCallback
        raise Exception("Can't find any matching TopicCallback for " + topic)

    # LOG
    def LogSource(self) -> str:
        return "MQTT"

    # NORMALIZE
    @staticmethod
    def NormalizeTopic(entityDataId) -> str:
        return entityDataId.replace(".", "/")
