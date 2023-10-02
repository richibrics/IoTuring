from __future__ import annotations
import os
import json
import yaml
import re
import time
from typing import Callable

from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.EntityData import EntityCommand, EntityData, EntitySensor
from IoTuring.Logger.LogObject import LogObject
from IoTuring.Protocols.MQTTClient.MQTTClient import MQTTClient
from IoTuring.Warehouse.Warehouse import Warehouse
from IoTuring.MyApp.App import App
from IoTuring.Logger import consts
from IoTuring.Entity.ValueFormat import ValueFormatter


INCLUDE_UNITS_IN_SENSORS = False
INCLUDE_UNITS_IN_EXTRA_ATTRIBUTES = True

SLEEP_TIME_NOT_CONNECTED_WHILE = 1

# That stands for: App name, Client name, EntityData Id
TOPIC_DATA_FORMAT = "{}/{}HomeAssistant/{}"
TOPIC_DATA_EXTRA_ATTRIBUTES_SUFFIX = "_extraattributes"
# That stands for: Entity data type, App name, EntityData Id
# to send configuration data
TOPIC_AUTODISCOVERY_FORMAT = "homeassistant/{}/{}/{}/config"

CONFIG_KEY_ADDRESS = "address"
CONFIG_KEY_PORT = "port"
CONFIG_KEY_NAME = "name"
CONFIG_KEY_USERNAME = "username"
CONFIG_KEY_PASSWORD = "password"
CONFIG_KEY_ADD_NAME_TO_ENTITY = "add_name"
CONFIG_KEY_USE_TAG_AS_ENTITY_NAME = "use_tag"

CONFIGURATION_SEND_LOOP_SKIP_NUMBER = 10

EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME = "entities.yaml"

LWT_TOPIC_SUFFIX = "LWT"
LWT_PAYLOAD_ONLINE = "ONLINE"
LWT_PAYLOAD_OFFLINE = "OFFLINE"
PAYLOAD_ON = consts.STATE_ON
PAYLOAD_OFF = consts.STATE_OFF


class HomeAssistantEntityBase(LogObject):
    """ Base class for all entities in HomeAssistantWarehouse """

    # Possible topics:
    availability_topic: str
    state_topic: str
    json_attributes_topic: str
    command_topic: str
    discovery_topic: str

    def __init__(self,
                 wh: "HomeAssistantWarehouse",
                 name: str = "",
                 id: str = ""
                 ) -> None:

        self.wh = wh
        self.name = name
        self.id = id
        self.unique_id = self.wh.clientName + "." + self.id

        self.supports_extra_attributes = False

        # Get custom info to the entity data, reading it from external file and accessing the information using the entity data name
        self.discovery_payload = \
            self.GetEntityDataCustomConfigurations(self.name)

        # Get data type:
        if "custom_type" in self.discovery_payload:
            self.data_type = self.discovery_payload.pop("custom_type")
        else:
            self.data_type = ""

        # Set name:
        self.SetDiscoveryPayloadName()

        # Set device info:
        device_info = {}
        device_info['name'] = self.wh.clientName
        device_info['model'] = self.wh.clientName
        device_info['identifiers'] = self.wh.clientName
        device_info['manufacturer'] = App.getName() + " by " + App.getVendor()
        device_info['sw_version'] = App.getVersion()

        self.discovery_payload['device'] = device_info
        self.discovery_payload['unique_id'] = self.unique_id

    def SetDefaultDataType(self, data_type: str) -> None:
        """ Set data type if not set previously """
        self.data_type = self.data_type or data_type
        if self.data_type in ["binary_sensor", "switch"]:
            self.SetDefaultDiscoveryPayload("payload_on", PAYLOAD_ON)
            self.SetDefaultDiscoveryPayload("payload_off", PAYLOAD_OFF)
        # Set discovery topic here, data_type is finalized:
        self.SetDiscoveryTopic()

    def SetDefaultDiscoveryPayload(self, key: str, value: str) -> None:
        """ Set value if not set already """
        if key in self.discovery_payload:
            self.discovery_payload[key] = self.discovery_payload[key] or value
        else:
            self.discovery_payload[key] = value

    def SetDiscoveryPayloadName(self) -> None:
        """ Set the name in the discovery payload if not set already """
        self.SetDefaultDiscoveryPayload("name", self.name)

        if self.wh.addNameToEntityName:
            self.discovery_payload["name"] = f"{self.wh.clientName} {self.discovery_payload['name']}"

    def AddTopic(self, topic_name: str, topic_path: str = ""):
        """ Add topic to the HA entity """
        if not topic_path:
            topic_path = getattr(self, "default_topics")[topic_name]

        # Add as an attribute:
        setattr(self, topic_name, topic_path)
        # Add to the discovery payload:
        self.discovery_payload[topic_name] = topic_path

    def SendTopicData(self, topic, data) -> None:
        self.wh.client.SendTopicData(topic, data)

    def SetDiscoveryTopic(self) -> None:
        """ Set the discovery topic attribute"""
        self.discovery_topic = self.wh.NormalizeTopic(TOPIC_AUTODISCOVERY_FORMAT.format(
            self.data_type, App.getName(), self.unique_id.replace(".", "_")))

    def GetEntityDataCustomConfigurations(self, entityDataName) -> dict:
        """ Add custom info to the entity data, reading it from external file and accessing the information using the entity data name """

        # if resource_file:
        config_path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME)
        with open(config_path) as yaml_data:

            data = yaml.safe_load(yaml_data.read())

            # Try exact match:
            try:
                return data[entityDataName]
            except KeyError:
                # No exact match, try regex:
                for entityData, entityDataConfiguration in data.items():
                    # entityData may be the correct name, or a regex expression that should return something applied to the real name
                    if re.search(entityData, entityDataName):
                        # merge payload and additional configurations
                        return entityDataConfiguration
        return {}  # if nothing found


class HomeAssistantEntity(HomeAssistantEntityBase):
    """ Base class for entity based sensors and commands in HomeAssistantWarehouse """

    def __init__(self, entityData: EntityData, wh: "HomeAssistantWarehouse") -> None:

        self.entityData = entityData
        self.entity = self.entityData.GetEntity()

        super().__init__(
            wh=wh,
            name=self.entity.GetEntityNameWithTag() + " - " +
            self.entityData.GetKey(),
            id=self.entityData.GetId()
        )

        # Custom payload from entities:
        self.discovery_payload.update(self.entityData.GetCustomPayload())

        # Default topics:
        self.default_topics = {
            "availability_topic": self.wh.MakeValuesTopic(LWT_TOPIC_SUFFIX),
            "state_topic": self.MakeEntityDataTopic(self.entityData),
            "json_attributes_topic": self.MakeEntityDataExtraAttributesTopic(self.entityData),
            "command_topic": self.MakeEntityDataTopic(self.entityData)
        }

        # Availability:
        self.AddTopic("availability_topic")
        self.discovery_payload["payload_available"] = LWT_PAYLOAD_ONLINE
        self.discovery_payload["payload_not_available"] = LWT_PAYLOAD_OFFLINE

    def SetDiscoveryPayloadName(self) -> None:
        """ Set discovery payload name """

        # Use Tag only as name:
        if self.wh.useTagAsEntityName and self.entity.GetEntityTag():
            self.discovery_payload["name"] = self.entity.GetEntityTag()

        else:
            # Add key only if more than one entityData, and it doesn't have a tag:
            if not self.entity.GetEntityTag() and \
                    len(self.entity.GetAllUnconnectedEntityData()) > 1:

                formatted_key = self.entityData.GetKey().capitalize().replace("_", " ")

                payload_name = f"{self.entity.GetEntityName()} - {formatted_key}"

            else:
                # Default name:
                payload_name = self.entity.GetEntityNameWithTag()

            self.SetDefaultDiscoveryPayload("name", payload_name)

        return super().SetDiscoveryPayloadName()

    def MakeEntityDataTopic(self, entityData: EntityData) -> str:
        """ Uses MakeValuesTopic but receives an EntityData to manage itself its id"""
        return self.wh.MakeValuesTopic(entityData.GetId())

    def MakeEntityDataExtraAttributesTopic(self, entityData: EntityData) -> str:
        """ Uses MakeValuesTopic but receives an EntityData to manage itself its id, appending a suffix to distinguish
            the extra attrbiutes from the original value """
        return self.wh.MakeValuesTopic(entityData.GetId() + TOPIC_DATA_EXTRA_ATTRIBUTES_SUFFIX)


class HomeAssistantSensor(HomeAssistantEntity):

    def __init__(self,  entityData: EntitySensor, wh: "HomeAssistantWarehouse") -> None:
        super().__init__(entityData=entityData, wh=wh)

        self.entitySensor = entityData
        self.supports_extra_attributes = self.entitySensor.DoesSupportExtraAttributes()

        # Default data type:
        self.SetDefaultDataType("sensor")

        # State topic for all sensors
        self.AddTopic("state_topic")

        if self.supports_extra_attributes:
            self.AddTopic("json_attributes_topic")

        # Extra payload for sensors:
        self.discovery_payload['expire_after'] = 600  # TODO Improve

    def SendValues(self):
        """ Send values of the sensor to the state topic """
        if self.entitySensor.HasValue():
            sensor_value = ValueFormatter.FormatValue(
                self.entitySensor.GetValue(),
                self.entitySensor.GetValueFormatterOptions(),
                INCLUDE_UNITS_IN_SENSORS)

            self.SendTopicData(self.state_topic, sensor_value)

            if self.supports_extra_attributes and \
                    self.entitySensor.HasExtraAttributes():
                formattedExtraAttributes = self.entitySensor.GetFormattedExtraAtributes(
                    INCLUDE_UNITS_IN_EXTRA_ATTRIBUTES)
                self.SendTopicData(
                    self.json_attributes_topic,
                    json.dumps(formattedExtraAttributes))


class HomeAssistantCommand(HomeAssistantEntity):
    def __init__(self, entityData: EntityCommand, wh: "HomeAssistantWarehouse") -> None:
        super().__init__(entityData=entityData, wh=wh)

        self.entityCommand = entityData

        self.AddTopic("availability_topic")
        self.AddTopic("command_topic")

        self.connected_sensor = self.GetConnectedSensor()

        if self.connected_sensor:
            self.SetDefaultDataType("switch")
            # Get discovery payload from connected sensor?
            for payload_key in self.connected_sensor.discovery_payload:
                if payload_key not in self.discovery_payload:
                    self.discovery_payload[payload_key] = self.connected_sensor.discovery_payload[payload_key]
        else:
            # Button as default data type:
            self.SetDefaultDataType("button")

        self.command_callback = self.GenerateCommandCallback()

    def GetConnectedSensor(self) -> HomeAssistantSensor | None:
        """ Get the connected sensor of this command """
        if self.entityCommand.SupportsState():
            return HomeAssistantSensor(
                entityData=self.entityCommand.GetConnectedEntitySensor(),
                wh=self.wh)
        else:
            return None

    def GenerateCommandCallback(self) -> Callable:
        """ Generate the callback function """
        def CommandCallback(message):
            status = self.entityCommand.CallCallback(message)
            if status and self.wh.client.IsConnected():
                if self.connected_sensor:
                    # Only set value if it was already set, to exclude optimistic switches
                    if self.connected_sensor.entitySensor.HasValue():
                        self.Log(self.LOG_DEBUG, "Switch callback: sending state to " +
                                 self.connected_sensor.state_topic)
                        self.SendTopicData(
                            self.connected_sensor.state_topic, message.payload.decode('utf-8'))
        return CommandCallback


class LwtSensor(HomeAssistantEntityBase):
    def __init__(self, wh: "HomeAssistantWarehouse") -> None:
        super().__init__(
            wh=wh,
            name="Connectivity",
            id="connectivity"
        )

        # topics:
        self.AddTopic("state_topic", self.wh.MakeValuesTopic(LWT_TOPIC_SUFFIX))

        self.discovery_payload["payload_on"] = LWT_PAYLOAD_ONLINE
        self.discovery_payload["payload_off"] = LWT_PAYLOAD_OFFLINE

        self.SetDiscoveryTopic()

    def SendValues(self):
        self.SendTopicData(self.state_topic, LWT_PAYLOAD_ONLINE)


class HomeAssistantWarehouse(Warehouse):
    NAME = "HomeAssistant"

    def Start(self):
        #  I configure my Warehouse with configurations
        self.clientName = self.GetFromConfigurations(CONFIG_KEY_NAME)
        self.client = MQTTClient(self.GetFromConfigurations(CONFIG_KEY_ADDRESS),
                                 self.GetFromConfigurations(CONFIG_KEY_PORT),
                                 self.GetFromConfigurations(CONFIG_KEY_NAME),
                                 self.GetFromConfigurations(
                                     CONFIG_KEY_USERNAME),
                                 self.GetFromConfigurations(CONFIG_KEY_PASSWORD))
        self.client.LwtSet(self.MakeValuesTopic(
            LWT_TOPIC_SUFFIX), LWT_PAYLOAD_OFFLINE)

        self.client.AsyncConnect()

        self.addNameToEntityName = self.GetTrueOrFalseFromConfigurations(
            CONFIG_KEY_ADD_NAME_TO_ENTITY)

        self.useTagAsEntityName = self.GetTrueOrFalseFromConfigurations(
            CONFIG_KEY_USE_TAG_AS_ENTITY_NAME)

        # Entities store:
        self.homeAssistantEntities = {
            "commands": [],
            "sensors": [],
            "connected_sensors": []
        }

        self.CollectEntityData()

        self.RegisterEntityCommands()

        self.loopCounter = 0

        super().Start()  # Then run other inits (start the Loop method for example)

    def CollectEntityData(self) -> None:
        """ Collect entities and save them ass hass entities """

        # Add the Lwt sensor:
        self.homeAssistantEntities["sensors"].append(LwtSensor(self))

        # Add real entities:
        for entity in self.GetEntities():
            for entityData in entity.GetAllUnconnectedEntityData():

                # It's a command:
                if isinstance(entityData, EntityCommand):
                    hasscommand = HomeAssistantCommand(entityData, self)
                    if hasscommand.connected_sensor:
                        self.homeAssistantEntities["connected_sensors"].append(
                            hasscommand.connected_sensor)
                    self.homeAssistantEntities["commands"].append(hasscommand)

                # It's a sensor:
                elif isinstance(entityData, EntitySensor):
                    self.homeAssistantEntities["sensors"].append(
                        HomeAssistantSensor(entityData, self))

                else:
                    raise Exception(f"Unkown EntityData! {entityData}")

    def RegisterEntityCommands(self):
        """ Add EntityCommands to the MQTT client (subscribe to them) """
        for hasscommand in self.homeAssistantEntities["commands"]:
            self.client.AddNewTopicToSubscribeTo(
                hasscommand.command_topic, hasscommand.command_callback)
            self.Log(
                self.LOG_DEBUG, f"{hasscommand.id} subscribed to {hasscommand.command_topic}")

    def Loop(self):

        while (not self.client.IsConnected()):
            time.sleep(SLEEP_TIME_NOT_CONNECTED_WHILE)

        # Mechanism to call the function to send discovery data every CONFIGURATION_SEND_LOOP_SKIP_NUMBER loop
        if self.loopCounter == 0:
            self.SendEntityDataConfigurations()

        # Every time I send data, every X also configurations
        self.loopCounter = (
            self.loopCounter+1) % CONFIGURATION_SEND_LOOP_SKIP_NUMBER

        # Send sensor values:
        for hasssensor in self.homeAssistantEntities["sensors"] + self.homeAssistantEntities["connected_sensors"]:
            hasssensor.SendValues()

    def SendEntityDataConfigurations(self):
        """ Send discovery """
        for hassentity in self.homeAssistantEntities["commands"] + self.homeAssistantEntities["sensors"]:
            topic = hassentity.discovery_topic
            payload = hassentity.discovery_payload

            self.client.SendTopicData(topic, json.dumps(payload))

    def MakeValuesTopic(self, topic_suffix: str) -> str:
        """ Prepares a topic, including the app name, the client name and finally a passed id """
        return self.NormalizeTopic(TOPIC_DATA_FORMAT.format(App.getName(), self.clientName, topic_suffix))

    @staticmethod
    def NormalizeTopic(topicstring: str) -> str:
        """ Home assistant requires stricter topic names """
        # Remove non ascii characters:
        topicstring=topicstring.encode("ascii", "ignore").decode()
        return MQTTClient.NormalizeTopic(topicstring).replace(" ", "_")

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        preset.AddEntry("Home assistant MQTT broker address",
                        CONFIG_KEY_ADDRESS, mandatory=True)
        preset.AddEntry("Port", CONFIG_KEY_PORT, default=1883)
        preset.AddEntry("Client name", CONFIG_KEY_NAME, mandatory=True)
        preset.AddEntry("Username", CONFIG_KEY_USERNAME, default="")
        preset.AddEntry("Password", CONFIG_KEY_PASSWORD, default="")
        preset.AddEntry("Add computer name to entity name ? Y/N",
                        CONFIG_KEY_ADD_NAME_TO_ENTITY, default="Y")
        preset.AddEntry("Use tag as entity name for multi instance entities? Y/N",
                        CONFIG_KEY_USE_TAG_AS_ENTITY_NAME, default="N")
        return preset
