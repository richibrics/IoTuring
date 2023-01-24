from IoTuring.Logger.LogObject import LogObject

# EntitySensor extra attribute aren't read from all the warehouses 

class EntityData(LogObject):

    def __init__(self, entity, key):
        self.entityId = entity.GetEntityId()
        self.id = self.entityId + "." + key
        self.key = key
        self.entity = entity

    def GetEntity(self):
        return self.entity

    def GetId(self):
        return self.id

    def GetKey(self):
        return self.key

    def LogSource(self):
        return self.GetId()


class EntitySensor(EntityData):

    def __init__(self, entity, key, supportsExtraAttributes = False):
        EntityData.__init__(self, entity, key)
        self.supportsExtraAttributes = supportsExtraAttributes
        self.value = None
        self.extraAttributes = None

    def DoesSupportExtraAttributes(self):
        return self.supportsExtraAttributes

    def GetValue(self):
        return self.value

    def SetValue(self, value):
        value = str(value)
        self.Log(self.LOG_DEBUG, "Set to " + value)
        self.value = value
        return self.value

    def HasValue(self):
        """ True if self.value isn't empty """
        return self.value is not None

    def GetExtraAttributes(self):
        if self.supportsExtraAttributes == False:
            raise Exception("This entity sensor does not support extra attributes. Please specify it when initializing the sensor.")
        return self.extraAttributes
    
    def HasExtraAttributes(self):
        """ True if self.extraAttributes isn't empty """
        return self.extraAttributes is not None
    
    def SetExtraAttributes(self, _dict):
        # a dict with (attribute_name: value) that is compatible only with certain warehouses
        if self.supportsExtraAttributes == False:
            raise Exception("This entity sensor does not support extra attributes. Please specify it when initializing the sensor.")
        self.extraAttributes = _dict



class EntityCommand(EntityData):

    def __init__(self, entity, key, callbackFunction, connectedEntitySensorKey = None):
        """
        If a key for the entity sensor is passed, warehouses that support it use this command as a switch with state.
        Better to register the sensor before this command to avoud unexpected behaviours.
        """
        EntityData.__init__(self, entity, key)
        self.callbackFunction = callbackFunction
        self.connectedEntitySensorKey = connectedEntitySensorKey

    def SupportsState(self):
        return self.connectedEntitySensorKey is not None
    
    def GetConnectedEntitySensor(self):
        """ Returns the entity sensor connected to this command, if this command supports state.
            Otherwise returns None. """
        return self.GetEntity().GetEntitySensorByKey(self.connectedEntitySensorKey)

    def CallCallback(self, message):
        """ Safely run callback for this command, passing the message (a paho.mqtt.client.MQTTMessage).
            Reutrns True if callback was run correctly, False if an error occurred."""
        self.Log(self.LOG_DEBUG, "Callback")
        try:
            self.RunCallback(message)
            return True
        except Exception as e:
            self.Log(self.LOG_ERROR, "Error while running callback: " + str(e))
            return False

    def RunCallback(self, message):
        """ Called only by CallCallback. 
            Run callback for this command, passing the message (a paho.mqtt.client.MQTTMessage) """
        self.callbackFunction(message)
