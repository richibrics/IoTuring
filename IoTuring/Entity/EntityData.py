from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from IoTuring.Entity.Entity import Entity

from IoTuring.Logger.LogObject import LogObject
from IoTuring.Entity.ValueFormat import ValueFormatter

# EntitySensor extra attribute aren't read from all the warehouses


class EntityData(LogObject):

    def __init__(self, entity: Entity, key, customPayload={}) -> None:
        self.entityId = entity.GetEntityId()
        self.id = self.entityId + "." + key
        self.key = key
        self.entity = entity
        self.customPayload = customPayload

    def GetEntity(self) -> Entity:
        return self.entity

    def GetId(self):
        return self.id

    def GetKey(self):
        return self.key

    def LogSource(self):
        return self.GetId()

    def GetCustomPayload(self):
        return self.customPayload


class EntitySensor(EntityData):

    value: str | int | float
    extraAttributes: list[ExtraAttribute]

    def __init__(self, entity, key,
                 valueFormatterOptions=None,
                 supportsExtraAttributes=False,
                 customPayload={}):
        """
        If supportsExtraAttributes is True, the entity sensor can have extra attributes.
        valueFormatterOptions is a IoTuring.Entity.ValueFormat.ValueFormatterOptions object.
        CustomPayload overrides HomeAssistant discovery configuration
        """
        EntityData.__init__(self, entity, key, customPayload)
        self.supportsExtraAttributes = supportsExtraAttributes
        self.valueFormatterOptions = valueFormatterOptions

    def DoesSupportExtraAttributes(self) -> bool:
        return self.supportsExtraAttributes

    def GetValueFormatterOptions(self):
        return self.valueFormatterOptions

    def GetValue(self) -> str | int | float:
        if self.HasValue():
            return self.value
        else:
            raise Exception("No value for this sensor!")

    def SetValue(self, value) -> None:
        self.Log(self.LOG_DEBUG, "Set to " + str(value))
        self.value = value

    def HasValue(self) -> bool:
        """ True if self.value isn't empty """
        return hasattr(self, "value")

    def GetExtraAttributes(self) -> list[ExtraAttribute]:
        """ Get extra attribute objects as a list """
        if not self.supportsExtraAttributes:
            raise Exception(
                "This entity sensor does not support extra attributes. Please specify it when initializing the sensor.")
        elif not self.HasExtraAttributes():
            raise Exception(
                "No extra attribute set yet!"
            )
        return self.extraAttributes

    def GetFormattedExtraAtributes(self, includeUnit: bool) -> dict[str, str]:
        """ Get extra attributes names and formatted values as a dict """
        formattedExtraAttributes = {}
        for extraAttr in self.GetExtraAttributes():
            formatted_value = ValueFormatter.FormatValue(
                extraAttr.GetValue(),
                extraAttr.GetValueFormatterOptions(),
                includeUnit)
            formattedExtraAttributes[extraAttr.GetName()] = formatted_value
        return formattedExtraAttributes

    def HasExtraAttributes(self):
        """ True if self.extraAttributes isn't empty """
        return hasattr(self, "extraAttributes")

    def SetExtraAttribute(self, attribute_name, attribute_value, valueFormatterOptions=None):
        if not self.supportsExtraAttributes:
            raise Exception(
                "This entity sensor does not support extra attributes. Please specify it when initializing the sensor.")
        if not self.HasExtraAttributes():
            self.extraAttributes = []

        # If the Attribute does not already exists, create it, otherwise update it
        extraAttributeObj = next(
            (attr for attr in self.extraAttributes if attr.GetName() == attribute_name), None)
        if not extraAttributeObj:
            self.extraAttributes.append(ExtraAttribute(
                attribute_name, attribute_value, valueFormatterOptions))
        else:
            extraAttributeObj.SetValue(attribute_value)


class EntityCommand(EntityData):

    def __init__(self, entity: Entity, key: str, callbackFunction: Callable,
                 connectedEntitySensorKeys: str | list = [],
                 customPayload={}):
        """Create a new EntityCommand.

        If key or keys for the entity sensor is passed, warehouses that support it can use this command as a switch with state.
        Order of sensors matter, first sensors state topic will be used.
        Better to register the sensors before this command to avoid unexpected behaviours.

        Args:
            entity (Entity): The entity this command belongs to.
            key (str): The KEY of this command
            callbackFunction (Callable): Function to be called
            connectedEntitySensorKeys (str | list, optional): A key to a sensor or a list of keys. Defaults to [].
            customPayload (dict, optional): Overrides HomeAssistant discovery configuration. Defaults to {}.
        """

        EntityData.__init__(self, entity, key, customPayload)
        self.callbackFunction = callbackFunction
        self.connectedEntitySensorKeys = connectedEntitySensorKeys if isinstance(
            connectedEntitySensorKeys, list) else [connectedEntitySensorKeys]

    def SupportsState(self) -> bool:
        """ True if this command supports state (has a connected sensors) """
        return bool(self.connectedEntitySensorKeys)

    def GetConnectedEntitySensors(self) -> list[EntitySensor]:
        """ Returns the entity sensors connected to this command. Returns empty list if none found. """
        return [self.GetEntity().GetEntitySensorByKey(key) for key in self.connectedEntitySensorKeys]

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


class ExtraAttribute():
    def __init__(self, name, value, valueFormatterOptions=None):
        self.name = name
        self.value = value
        self.valueFormatterOptions = valueFormatterOptions

    def GetName(self):
        return self.name

    def GetValue(self):
        return self.value

    def GetValueFormatterOptions(self):
        return self.valueFormatterOptions

    def HasValueFormatterOptions(self):
        return self.valueFormatterOptions is not None

    def SetValue(self, value):
        self.value = value
