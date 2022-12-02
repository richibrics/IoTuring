import psutil
from IoTuring.Entity.Entity import Entity 
import signal, sys
import time

TOPIC_STATE = 'state'


class State(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC_STATE)
        signal.signal(signal.SIGINT, self.ExitSignal)


    def Update(self):
        self.SetTopicValue(TOPIC_STATE, self.consts.ONLINE_STATE)

    def SendOfflineState(self):
        self.mqtt_client.SendTopicData(self.SelectTopic(TOPIC_STATE),self.consts.OFFLINE_STATE)

    def ExitSignal(self,sig, frame):
        # Before exiting I send an offline message to the state_topic if prese
        print("\r", end="") # This removes the Control-C symbol (^C)
        self.Log(self.Logger.LOG_INFO,'Let me send the Offline state message')
        self.SendOfflineState()
        time.sleep(1)
        self.Log(self.Logger.LOG_INFO,"All done, goodbye !")
        sys.exit(0)
        