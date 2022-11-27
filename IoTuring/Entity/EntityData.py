from IoTuring.Logger.LogObject import LogObject


class EntityData(LogObject):

    def __init__(self, entity, key):
        self.entityId = entity.GetEntityId()
        self.id = self.entityId + "." + key
        self.key = key

    def GetId(self):
        return self.id

    def GetKey(self):
        return self.key

    def LogSource(self):
        return self.GetId()


class EntitySensor(EntityData):

    def __init__(self, entity, key):
        EntityData.__init__(self, entity, key)
        self.value = None

    def SetValue(self, value):
        value = str(value)
        self.Log(self.LOG_DEBUG, "Set to " + value)
        self.value = value
        return self.value

    def GetValue(self):
        return self.value

    def HasValue(self):
        """ True if self.value isn't empty """
        return self.value is not None 

class EntityCommand(EntityData):

    def __init__(self, entity, key, callbackFunction):
        EntityData.__init__(self, entity, key)
        self.callbackFunction = callbackFunction

    def CallCallback(self, message):
        """ Safely run callback for this command, passing the message (a paho.mqtt.client.MQTTMessage) """
        self.Log(self.LOG_DEBUG, "Callback")
        try:
            self.RunCallback(message)
        except Exception as e:
            self.Log(self.LOG_ERROR, "Error while running callback: " + str(e))

    def RunCallback(self, message):
        """ Called only by CallCallback. 
            Run callback for this command, passing the message (a paho.mqtt.client.MQTTMessage) """
        self.callbackFunction(message)
