from Logger.Logger import Logger
from App.App import App
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

"""

MQTTClient Operations:
- Init
- AsyncConnect
- SendTopicData
- AddNewTopicToSubscribeTo

"""

class MQTTClient:
    client = None
    connected = False

    # After the init, you have to connect with AsyncConnect !
    def __init__(self,address,port=1883,name=None,username="",password="") -> None:
        self.address = address
        self.port = port
        self.name = name
        self.username = username
        self.password = password

        if self.name == None:
            self.name = App.getName()

        # Lists for topic to which I should subscribe and topics I'm already subscribed to
        self.topicsToSubscribe = [] # When I'm connected/reconnected, I resub to these
        self.topicsSubscribed = []

        
        self.Log(Logger.LOG_INFO, 'Preparing MQTT client')
        self.SetupClient()


    def SetupClient(self):
        self.client = mqtt.Client(self.name)

        if self.username != "" and self.password != "":
            self.client.username_pw_set(self.username, self.password)

        # Assign event callbacks
        self.client.on_connect = self.Event_OnClientConnect
        self.client.on_disconnect = self.Event_OnClientDisconnect
        self.client.on_message = self.Event_OnMessageReceive


    def AsyncConnect(self):
        self.Log(Logger.LOG_INFO, 'MQTT Client ready to connect to the broker')
        # Connect async to the broker
        # If broker is not reachable wait till he's reachable
        self.client.connect_async(self.address, port=self.port)
        self.client.loop_start()



    # EVENTS

    def Event_OnClientConnect(self, client, userdata, flags, rc):
        if rc == 0:  # Connections is OK
            self.Log(Logger.LOG_INFO, "Connection established")
            self.connected = True
            self.SubscribeToAllTopics()
        else:
            self.Log(Logger.LOG_ERROR, "Connection error")

    def Event_OnClientDisconnect(self, client, userdata, rc):
        self.Log(Logger.LOG_ERROR, "Connection lost")
        self.connected = False
        self.topicsSubscribed.clear()

    def Event_OnMessageReceive(self, client, userdata, message):
        pass # TODO When implementing callbacks



    # INCOMING MESSAGES PART

    def SendTopicData(self, topic, data):
        self.client.publish(topic, data)

    # OUTCOMING MESSAGES PART / SUBSCRIBE

    def AddNewTopicToSubscribeTo(self, topic, callbackCommand):
        # TODO Implement
        # self.topics.append({'topic': topic, 'callback': callbackCommand})
        self.SubscribeToTopic(topic)

    def SubscribeToAllTopics(self):
        # TODO Implement when you know how to implement callbacks
        # for topic in self.topicsToSubscribe:
        #     self.SubscribeToTopic(TOPIC_WHICH_ONE_?)
        pass

    def SubscribeToTopic(self, topic):
        # TODO Check this function
        if topic not in self.topicsSubscribed and self.connected:
            self.topicsSubscribed.append(topic)
            self.client.subscribe(topic, 0)

    def UnsubscribeToTopic(self,topic):
        # TODO Implement
        pass
    
    # LOG

    def Log(self, messageType, message):
        Logger().getInstance().Log(messageType, 'MQTT', message)