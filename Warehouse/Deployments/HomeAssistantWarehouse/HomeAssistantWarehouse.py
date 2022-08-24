import inspect
import os
from Configurator.MenuPreset import MenuPreset
from Protocols.MQTTClient.MQTTClient import MQTTClient
from Warehouse.Warehouse import Warehouse
from MyApp.App import App
import json
import yaml
import re

TOPIC_DATA_FORMAT = "{}/{}HomeAssistant/{}"  # That stands for: App name, Client name, EntityData Id
TOPIC_AUTODISCOVERY_FORMAT = "homeassistant/{}/{}/{}/config"  # That stands for: Entity data type, App name, EntityData Id

CONFIG_KEY_ADDRESS = "address"
CONFIG_KEY_PORT = "port"
CONFIG_KEY_NAME = "name"
CONFIG_KEY_USERNAME = "username"
CONFIG_KEY_PASSWORD = "password"
CONFIG_KEY_ADD_NAME_TO_ENTITY = "add_name"

CONFIGURATION_SEND_LOOP_SKIP_NUMBER = 10

EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME = "entities.yaml"
EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE = "custom_type"

class HomeAssistantWarehouse(Warehouse):
    NAME = "HomeAssistant"

    def Start(self):
        # I configure my Warehouse with configurations
        self.clientName = self.GetFromConfigurations(CONFIG_KEY_NAME)
        self.client = MQTTClient(self.GetFromConfigurations(CONFIG_KEY_ADDRESS),
                                    self.GetFromConfigurations(CONFIG_KEY_PORT),
                                    self.GetFromConfigurations(CONFIG_KEY_NAME),
                                    self.GetFromConfigurations(CONFIG_KEY_USERNAME),
                                    self.GetFromConfigurations(CONFIG_KEY_PASSWORD))
                                    
        self.client.AsyncConnect()

        self.addNameToEntityName = self.GetTrueOrFalseFromConfigurations(CONFIG_KEY_ADD_NAME_TO_ENTITY)

        self.RegisterEntityCommands()

        self.loopCounter = 0

        super().Start() # Then run other inits (start the loop for example)

    def RegisterEntityCommands(self):
        """ Add EntityCommands to the MQTT client (subscribe to them) """
        for entity in self.GetEntities():
            for entityCommand in entity.GetEntityCommands():
                self.client.AddNewTopicToSubscribeTo(
                    self.MakeValuesTopic(entityCommand), entityCommand.CallCallback)
                self.Log(self.LOG_DEBUG, entityCommand.GetId() + " subscribed to " + self.MakeValuesTopic(entityCommand))

    def Loop(self):
        while(not self.client.IsConnected()):
            pass

        # Machanism to call the function to send discovery data every CONFIGURATION_SEND_LOOP_SKIP_NUMBER loop
        if self.loopCounter == 0:
            self.SendEntityDataConfigurations()
        self.loopCounter = (self.loopCounter+1)%CONFIGURATION_SEND_LOOP_SKIP_NUMBER # Every time I send data, every X also configurations

        # Sensor value
        self.SendSensorsValues()


    def SendSensorsValues(self):
        """ Here I send sensor's data (command callbacks are not managed here) """
        for entity in self.GetEntities():
            for entitySensor in entity.GetEntitySensors():
                if(entitySensor.HasValue()):
                    self.client.SendTopicData(self.MakeValuesTopic(
                        entitySensor), entitySensor.GetValue())

    def SendEntityDataConfigurations(self):
        for entity in self.GetEntities():
            for entityData in entity.GetAllEntityData():
                data_type = ""
                autoDiscoverySendTopic = ""
                payload = {}
                payload['name'] = entity.GetEntityNameWithTag() + " - " + entityData.GetKey()

                # check the data type: can be edited from custom configurations
                if entityData in entity.GetEntitySensors(): # it's an EntitySensorData
                    data_type = "sensor"
                else: # it's a EntityCommandData
                    data_type = "switch"

                # add custom info to the entity data, reading it from external file and accessing the information using the entity data name
                payload = self.AddEntityDataCustomConfigurations(payload['name'], payload)
                # check if custom configs have a new data type
                if EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE in payload:
                    data_type = payload[EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE]
                    payload.pop(EXTERNAL_ENTITY_DATA_CONFIGURATION_KEY_CUSTOM_TYPE)

                if self.addNameToEntityName:
                    payload['name'] = self.clientName + " " + payload['name']

                payload['device'] = self.MakeApplicationConfiguration()
                payload['unique_id'] = entityData.GetId()

                # TODO Add all customizable configurations

                if entityData in entity.GetEntitySensors(): # it's an EntitySensorData
                    payload['expire_after']=600 # TODO Improve
                    payload['state_topic'] = self.MakeValuesTopic(entityData)
                    autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format(data_type,App.getName(),entityData.GetId().replace(".","_"))
                else: # it's a EntityCommandData
                    payload['command_topic'] = self.MakeValuesTopic(entityData)                    
                    autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format(data_type,App.getName(),entityData.GetId().replace(".","_"))

                # Send
                self.client.SendTopicData(autoDiscoverySendTopic,json.dumps(payload))

    
    def AddEntityDataCustomConfigurations(self, entityDataName, payload):
        """ Add custom info to the entity data, reading it from external file and accessing the information using the entity data name """
        with open(os.path.join(os.path.dirname(inspect.getfile(HomeAssistantWarehouse)), EXTERNAL_ENTITY_DATA_CONFIGURATION_FILE_FILENAME)) as yaml_data:
            data = yaml.safe_load(yaml_data.read())
            for entityData, entityDataConfiguration in data.items():
                # entityData may be the correct name, or a regex expression that should return something applied to the real name
                if re.search(entityData, entityDataName):
                    return  {**payload, **entityDataConfiguration} # merge payload and additional configurations
        return payload # if nothing found

    def MakeValuesTopic(self, entityData):
        return MQTTClient.NormalizeTopic(TOPIC_DATA_FORMAT.format(App.getName(), self.clientName, entityData.GetId()))

    def MakeApplicationConfiguration(self):  # Add device information
        device = {}
        device['name'] = self.clientName
        device['model'] = self.clientName
        device['identifiers'] = self.clientName
        device['manufacturer'] = App.getName() + " by " + App.getVendor()
        device['sw_version'] = App.getVendor()
        return device

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Home assistant MQTT broker address",CONFIG_KEY_ADDRESS,mandatory=True)
        preset.AddEntry("Port",CONFIG_KEY_PORT,default=1883)
        preset.AddEntry("Client name",CONFIG_KEY_NAME,mandatory=True)
        preset.AddEntry("Username",CONFIG_KEY_USERNAME,default="")
        preset.AddEntry("Password",CONFIG_KEY_PASSWORD,default="")
        preset.AddEntry("Add computer name to entity name ? Y/N",CONFIG_KEY_PASSWORD,default="Y")
        return preset