import inspect
import os
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Protocols.MQTTClient.MQTTClient import MQTTClient
from IoTuring.Warehouse.Warehouse import Warehouse
from IoTuring.MyApp.App import App
import json
import yaml
import re

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

CONFIGURATION_SEND_LOOP_SKIP_NUMBER = 10

EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME = "entities.yaml"
EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE = "custom_type"

LWT_TOPIC_SUFFIX = "LWT"
LWT_PAYLOAD_ONLINE = "ON"
LWT_PAYLOAD_OFFLINE = "OFF"


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

        self.RegisterEntityCommands()

        self.loopCounter = 0

        super().Start()  # Then run other inits (start the Loop method for example)

    def RegisterEntityCommands(self):
        """ Add EntityCommands to the MQTT client (subscribe to them) """
        for entity in self.GetEntities():
            for entityCommand in entity.GetEntityCommands():
                self.client.AddNewTopicToSubscribeTo(
                    self.MakeEntityDataTopic(entityCommand), entityCommand.CallCallback)
                self.Log(self.LOG_DEBUG, entityCommand.GetId(
                ) + " subscribed to " + self.MakeEntityDataTopic(entityCommand))

    def Loop(self):
        # Send online state
        self.client.SendTopicData(self.MakeValuesTopic(
            LWT_TOPIC_SUFFIX), LWT_PAYLOAD_ONLINE)

        while (not self.client.IsConnected()):
            pass

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
                    self.client.SendTopicData(self.MakeEntityDataTopic(
                        entitySensor), entitySensor.GetValue())
                if (entitySensor.HasExtraAttributes()):  # send as json
                    self.client.SendTopicData(self.MakeEntityDataExtraAttributesTopic(entitySensor),
                                              json.dumps(entitySensor.GetExtraAttributes()))

    def SendEntityDataConfigurations(self):
        self.SendLwtSensorConfiguration()
        for entity in self.GetEntities():
            for entityData in entity.GetAllEntityData():
                data_type = ""
                autoDiscoverySendTopic = ""
                payload = {}
                payload['name'] = entity.GetEntityNameWithTag() + " - " + \
                    entityData.GetKey()

                # check the data type: can be edited from custom configurations
                if entityData in entity.GetEntitySensors():  # it's an EntitySensorData
                    data_type = "sensor"
                else:  # it's a EntityCommandData
                    data_type = "button"

                # add custom info to the entity data, reading it from external file and accessing the information using the entity data name
                payload = self.AddEntityDataCustomConfigurations(
                    payload['name'], payload)
                # check if custom configs have a new data type
                if EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE in payload:
                    data_type = payload[EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE]
                    payload.pop(
                        EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE)

                if self.addNameToEntityName:
                    payload['name'] = self.clientName + " " + payload['name']

                payload['device'] = self.MakeApplicationConfiguration()
                payload['unique_id'] = self.clientName + \
                    "." + entityData.GetId()

                if entityData in entity.GetEntitySensors():  # it's an EntitySensorData
                    # If the sensor supports extra attributes, send them as JSON.
                    # So here I have to specify also the topic for those attrbitues
                    if entityData.DoesSupportExtraAttributes():
                        payload["json_attributes_topic"] = self.MakeEntityDataExtraAttributesTopic(
                            entityData)

                    payload['expire_after'] = 600  # TODO Improve
                    payload['state_topic'] = self.MakeEntityDataTopic(
                        entityData)
                    autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format(
                        data_type, App.getName(), payload['unique_id'].replace(".", "_"))
                else:  # it's a EntityCommandData
                    payload['command_topic'] = self.MakeEntityDataTopic(
                        entityData)
                    autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format(
                        data_type, App.getName(), payload['unique_id'].replace(".", "_"))

                # Add availability configuration
                payload["availability_topic"] = self.MakeValuesTopic(
                    LWT_TOPIC_SUFFIX)
                payload["payload_available"] = LWT_PAYLOAD_ONLINE
                payload["payload_not_available"] = LWT_PAYLOAD_OFFLINE

                # Send
                self.client.SendTopicData(
                    autoDiscoverySendTopic, json.dumps(payload))

    def SendLwtSensorConfiguration(self):
        """ Sends the same configuration as any other entity, but for the lwt message value (so we have
            a message with a value that isn't from an entity and we want to send discovery data for it) """
        lwt_discovery = {}
        lwt_discovery['name'] = "Connectivity"

        if self.addNameToEntityName:
            lwt_discovery['name'] = self.clientName + \
                " " + lwt_discovery['name']

        lwt_discovery['device'] = self.MakeApplicationConfiguration()
        lwt_discovery['unique_id'] = self.clientName + ".connectivity"
        lwt_discovery["device_class"] = "connectivity"
        lwt_discovery['state_topic'] = self.MakeValuesTopic(LWT_TOPIC_SUFFIX)

        lwt_discovery["payload_on"] = LWT_PAYLOAD_ONLINE
        lwt_discovery["payload_off"] = LWT_PAYLOAD_OFFLINE

        autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format(
            "binary_sensor", App.getName(), lwt_discovery['unique_id'].replace(".", "_"))

        # send
        self.client.SendTopicData(
            autoDiscoverySendTopic, json.dumps(lwt_discovery))

    def AddEntityDataCustomConfigurations(self, entityDataName, payload):
        """ Add custom info to the entity data, reading it from external file and accessing the information using the entity data name """
        with open(os.path.join(os.path.dirname(inspect.getfile(HomeAssistantWarehouse)), EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME)) as yaml_data:
            data = yaml.safe_load(yaml_data.read())
            for entityData, entityDataConfiguration in data.items():
                # entityData may be the correct name, or a regex expression that should return something applied to the real name
                if re.search(entityData, entityDataName):
                    # merge payload and additional configurations
                    return {**payload, **entityDataConfiguration}
        return payload  # if nothing found

    def MakeEntityDataTopic(self, entityData):
        """ Uses MakeValuesTopic but receives an EntityData to manage itself its id"""
        return self.MakeValuesTopic(entityData.GetId())

    def MakeEntityDataExtraAttributesTopic(self, entityData):
        """ Uses MakeValuesTopic but receives an EntityData to manage itself its id, appending a suffix to distinguish
            the extra attrbiutes from the original value """
        return self.MakeValuesTopic(entityData.GetId() + TOPIC_DATA_EXTRA_ATTRIBUTES_SUFFIX)

    def MakeValuesTopic(self, topic_suffix):
        """ Prepares a topic, including the app name, the client name and finally a passed id """
        return MQTTClient.NormalizeTopic(TOPIC_DATA_FORMAT.format(App.getName(), self.clientName, topic_suffix))

    def MakeApplicationConfiguration(self):  # Add device information
        device = {}
        device['name'] = self.clientName
        device['model'] = self.clientName
        device['identifiers'] = self.clientName
        device['manufacturer'] = App.getName() + " by " + App.getVendor()
        device['sw_version'] = App.getVersion()
        return device

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Home assistant MQTT broker address",
                        CONFIG_KEY_ADDRESS, mandatory=True)
        preset.AddEntry("Port", CONFIG_KEY_PORT, default=1883)
        preset.AddEntry("Client name", CONFIG_KEY_NAME, mandatory=True)
        preset.AddEntry("Username", CONFIG_KEY_USERNAME, default="")
        preset.AddEntry("Password", CONFIG_KEY_PASSWORD, default="")
        preset.AddEntry("Add computer name to entity name ? Y/N",
                        CONFIG_KEY_ADD_NAME_TO_ENTITY, default="Y")
        return preset
