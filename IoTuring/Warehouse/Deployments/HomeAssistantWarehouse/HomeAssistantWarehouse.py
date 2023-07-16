import inspect
import os
import json
import yaml
import re
import time

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


class Topic:
    """ Base class for topic generation and sanitization """

    def __init__(self) -> None:
        self.clientName = ""

    def MakeEntityDataTopic(self, entityData: EntityData) -> str:
        """ Uses MakeValuesTopic but receives an EntityData to manage itself its id"""
        return self.MakeValuesTopic(entityData.GetId())

    def MakeEntityDataExtraAttributesTopic(self, entityData: EntityData) -> str:
        """ Uses MakeValuesTopic but receives an EntityData to manage itself its id, appending a suffix to distinguish
            the extra attrbiutes from the original value """
        return self.MakeValuesTopic(entityData.GetId() + TOPIC_DATA_EXTRA_ATTRIBUTES_SUFFIX)

    def MakeValuesTopic(self, topic_suffix: str) -> str:
        """ Prepares a topic, including the app name, the client name and finally a passed id """
        return self.NormalizeTopic(TOPIC_DATA_FORMAT.format(App.getName(), self.clientName, topic_suffix))

    @staticmethod
    def NormalizeTopic(topicstring: str) -> str:
        """ Home assistant requires stricter topic names """
        return MQTTClient.NormalizeTopic(topicstring).replace(" ", "_")


class AutoDiscovery(LogObject, Topic):
    """ Generate AutoDiscovery topic and payload """

    def __init__(self,
                 useTagAsEntityName: bool,
                 addNameToEntityName: bool,
                 clientName: str,
                 name: str = "",
                 entityData: EntityData | None = None,
                 ) -> None:

        # configurations:
        self.useTagAsEntityName = useTagAsEntityName
        self.addNameToEntityName = addNameToEntityName
        self.clientName = clientName

        self.payload = {}

        self.name = name
        self.id = self.name.lower()
        self.entityData = entityData
        self.data_sensor = None
        self.data_type = ""

        if self.entityData:
            self.entity = self.entityData.GetEntity()
            self.name = self.entity.GetEntityNameWithTag() + " - " + \
                self.entityData.GetKey()
            self.id = self.entityData.GetId()

        # Get custom info to the entity data, reading it from external file and accessing the information using the entity data name
        self.custom_config = self.GetEntityDataCustomConfigurations(self.name)

        # Get payload values
        self.GetName()
        self.GetDataType()
        self.GetTopicsAndPayloads()
        self.GetPayloadOverwrites()

        self.topic = self.NormalizeTopic(TOPIC_AUTODISCOVERY_FORMAT.format(
            self.data_type, App.getName(), self.payload['unique_id'].replace(".", "_")))

        self.Log(self.LOG_DEBUG, f"Discovery payload for {self.name}")
        self.Log(self.LOG_DEBUG, f"Autodiscovery topic: {self.topic}")
        self.Log(self.LOG_DEBUG, self.payload)

    def GetName(self) -> None:
        """ Generate entity name for the payload """
        if self.entityData:
            # Get the name:
            self.payload["name"] = self.entity.GetEntityNameWithTag()

            # Add key only if more than one entityData, and it doesn't have a tag:
            if not self.entity.GetEntityTag() and \
                    len(self.entity.GetAllUnconnectedEntityData()) > 1:

                formatted_key = self.entityData.GetKey().capitalize().replace("_", " ")
                self.payload["name"] += " - " + formatted_key

        else:
            self.payload["name"] = self.name

        # Get the name from custom config file:
        self.payload["name"] = self.GetCustomConfigValue(
            "name") or self.payload["name"]

        # Use Tag only as name:
        if self.useTagAsEntityName and self.entityData:
            if self.entity.GetEntityTag():
                self.payload["name"] = self.entity.GetEntityTag()

        # Add client name:
        if self.addNameToEntityName:
            self.payload["name"] = f"{self.clientName} {self.payload['name']}"

    def GetDataType(self) -> None:
        """ Get the data_type of the entity """
        # It's an EntityCommandData:
        if isinstance(self.entityData, EntityCommand):
            if self.entityData.SupportsState():
                self.data_type = "switch"
                self.data_sensor = self.entityData.GetConnectedEntitySensor()
            else:
                self.data_type = "button"

        # it's an EntitySensorData:
        elif isinstance(self.entityData, EntitySensor):
            self.data_type = "sensor"
            self.data_sensor = self.entityData

        # From config file:
        self.data_type = self.GetCustomConfigValue(
            "custom_type") or self.data_type

    def GetTopicsAndPayloads(self) -> None:
        """ Generate remaining payloads """
        self.payload['device'] = self.MakeApplicationConfiguration()
        self.payload['unique_id'] = self.clientName + \
            "." + self.id

        # Set lwt sensor:
        if not self.entityData:
            self.payload['state_topic'] = \
                self.MakeValuesTopic(LWT_TOPIC_SUFFIX)
            self.payload["payload_on"] = LWT_PAYLOAD_ONLINE
            self.payload["payload_off"] = LWT_PAYLOAD_OFFLINE

        else:
            # add configurations about sensors or switches (both have a state).
            # data_sensor is the entitysensor, or the connected sensor:
            if self.data_sensor:
                # extra attributes
                if self.data_sensor.DoesSupportExtraAttributes():
                    self.payload["json_attributes_topic"] = \
                        self.MakeEntityDataExtraAttributesTopic(
                            self.data_sensor)

                self.payload['expire_after'] = 600  # TODO Improve
                self.payload['state_topic'] = self.MakeEntityDataTopic(
                    self.data_sensor)

            # if it's a command (so button or switch), configure the topic where the command will be called
            if isinstance(self.entityData, EntityCommand):
                self.payload['command_topic'] = \
                    self.MakeEntityDataTopic(self.entityData)

            # Add default payloads (only for ON/OFF entities)
            if self.data_type in ["binary_sensor", "switch"]:
                self.payload['payload_on'] = PAYLOAD_ON
                self.payload['payload_off'] = PAYLOAD_OFF

            # Add availability configuration
            self.payload["availability_topic"] = self.MakeValuesTopic(
                LWT_TOPIC_SUFFIX)
            self.payload["payload_available"] = LWT_PAYLOAD_ONLINE
            self.payload["payload_not_available"] = LWT_PAYLOAD_OFFLINE

    def GetPayloadOverwrites(self) -> None:
        """ Overwrites from yaml file and from the entities itself """
        # Add remaining overwrites from custom config:
        self.payload.update(self.custom_config)

        # Override from custom entity payload config:
        if self.entityData:
            custom_payload = self.entityData.GetCustomPayload()
            if self.data_sensor:
                custom_payload = {**custom_payload, **
                                  self.data_sensor.GetCustomPayload()}
            self.payload.update(custom_payload)

    def GetCustomConfigValue(self, configName: str) -> str | None:
        """ Get configuration from yaml file """
        if configName in self.custom_config:
            return self.custom_config.pop(configName)
        else:
            return None

    def GetEntityDataCustomConfigurations(self, entityDataName) -> dict:
        """ Add custom info to the entity data, reading it from external file and accessing the information using the entity data name """
        with open(os.path.join(os.path.dirname(inspect.getfile(HomeAssistantWarehouse)), EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME)) as yaml_data:
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

    def MakeApplicationConfiguration(self):  # Add device information
        device = {}
        device['name'] = self.clientName
        device['model'] = self.clientName
        device['identifiers'] = self.clientName
        device['manufacturer'] = App.getName() + " by " + App.getVendor()
        device['sw_version'] = App.getVersion()
        return device


class HomeAssistantWarehouse(Warehouse, Topic):
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

        self.RegisterEntityCommands()

        self.loopCounter = 0

        super().Start()  # Then run other inits (start the Loop method for example)

    def RegisterEntityCommands(self):
        """ Add EntityCommands to the MQTT client (subscribe to them) """
        for entity in self.GetEntities():
            for entityCommand in entity.GetEntityCommands():
                self.client.AddNewTopicToSubscribeTo(
                    self.MakeEntityDataTopic(entityCommand), self.GenerateCommandCallback(entityCommand))
                self.Log(self.LOG_DEBUG, entityCommand.GetId(
                ) + " subscribed to " + self.MakeEntityDataTopic(entityCommand))

    def GenerateCommandCallback(self, entityCommand):
        """ Generates a lambda function that will become the command callback.
            Obviously this lamda will call the default callback of the command.
            But will also send the state to the state topic of the sensor relative to the command,
            in case the command has a sensor connected to it (= is a switch).
            This is needed to avoid status blinking on HA."""
        def CommandCallback(message):
            status = entityCommand.CallCallback(
                message)  # True: success, False: error
            if status and self.client.IsConnected():
                if entityCommand.SupportsState():

                    connected_sensor = entityCommand.GetConnectedEntitySensor()
                    # Only set value if it was already set, to exclude optimistic switches
                    if connected_sensor.HasValue():
                        sensor_topic = self.MakeEntityDataTopic(
                            connected_sensor)
                        self.Log(
                            self.LOG_DEBUG, "Switch callback: sending state to " + sensor_topic)
                        self.client.SendTopicData(
                            sensor_topic, message.payload.decode('utf-8'))
        return CommandCallback

    def Loop(self):
        # Send online state
        self.client.SendTopicData(self.MakeValuesTopic(
            LWT_TOPIC_SUFFIX), LWT_PAYLOAD_ONLINE)

        while (not self.client.IsConnected()):
            time.sleep(SLEEP_TIME_NOT_CONNECTED_WHILE)

        # Mechanism to call the function to send discovery data every CONFIGURATION_SEND_LOOP_SKIP_NUMBER loop
        if self.loopCounter == 0:
            self.SendEntityDataConfigurations()

        # Every time I send data, every X also configurations
        self.loopCounter = (
            self.loopCounter+1) % CONFIGURATION_SEND_LOOP_SKIP_NUMBER

        # Sensor value
        self.SendSensorsValues()

    def SendSensorsValues(self):
        """ Here I send sensor's data (command callbacks are not managed here) """
        for entity in self.GetEntities():
            for entitySensor in entity.GetEntitySensors():
                if (entitySensor.HasValue()):
                    topic = self.MakeEntityDataTopic(entitySensor)
                    value = ValueFormatter.FormatValue(
                        entitySensor.GetValue(),
                        entitySensor.GetValueFormatterOptions(),
                        INCLUDE_UNITS_IN_SENSORS)
                    self.client.SendTopicData(topic, value)  # send

                if (entitySensor.HasExtraAttributes()):
                    self.client.SendTopicData(self.MakeEntityDataExtraAttributesTopic(entitySensor),
                                              json.dumps(self.PrepareExtraAttributes(entitySensor)))

    def PrepareExtraAttributes(self, entitySensor):
        """ Prepare extra attributes to send to HA """
        extraAttributesDict = {}
        extraAttributes = entitySensor.GetExtraAttributes()
        for extraAttribute in extraAttributes:
            formatted_value = ValueFormatter.FormatValue(
                extraAttribute.GetValue(),
                extraAttribute.GetValueFormatterOptions(),
                INCLUDE_UNITS_IN_EXTRA_ATTRIBUTES)
            extraAttributesDict[extraAttribute.GetName()] = formatted_value
        return extraAttributesDict

    def SendEntityDataConfigurations(self):

        # Send lwt discovery:
        lwt_discovery = AutoDiscovery(
            name="Connectivity",
            useTagAsEntityName=self.useTagAsEntityName,
            addNameToEntityName=self.addNameToEntityName,
            clientName=self.clientName)
        self.client.SendTopicData(
            lwt_discovery.topic, json.dumps(lwt_discovery.payload))

        for entity in self.GetEntities():
            for entityData in entity.GetAllUnconnectedEntityData():

                entity_discovery = AutoDiscovery(
                    entityData=entityData,
                    useTagAsEntityName=self.useTagAsEntityName,
                    addNameToEntityName=self.addNameToEntityName,
                    clientName=self.clientName)
                self.client.SendTopicData(entity_discovery.topic,
                                          json.dumps(entity_discovery.payload))

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
