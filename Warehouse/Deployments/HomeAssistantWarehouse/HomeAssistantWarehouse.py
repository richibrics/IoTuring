from Configurator.MenuPreset import MenuPreset
from Protocols.MQTTClient.MQTTClient import MQTTClient
from Warehouse.Warehouse import Warehouse
from MyApp.App import App
import json

TOPIC_DATA_FORMAT = "{}/{}HomeAssistant/{}"  # That stands for: App name, Client name, EntityData Id
TOPIC_AUTODISCOVERY_FORMAT = "homeassistant/{}/{}/{}/config"  # That stands for: Entity data type, App name, EntityData Id

CONFIG_KEY_ADDRESS = "address"
CONFIG_KEY_PORT = "port"
CONFIG_KEY_NAME = "name"
CONFIG_KEY_USERNAME = "username"
CONFIG_KEY_PASSWORD = "password"

CONFIGURATION_SEND_LOOP_SKIP_NUMBER = 10

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
                autoDiscoverySendTopic = ""
                payload = {}
                payload['name'] = entity.GetEntityNameWithTag() + " - " + entityData.GetKey()
                payload['device'] = self.MakeApplicationConfiguration()
                payload['unique_id'] = entityData.GetId()

                # TODO Add all customizable configurations

                if entityData in entity.GetEntitySensors(): # it's an EntitySensorData
                    payload['expire_after']=600 # TODO Improve
                    payload['state_topic'] = self.MakeValuesTopic(entityData)
                    autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format("sensor",App.getName(),entityData.GetId().replace(".","_"))
                else: # it's a EntityCommandData
                    payload['command_topic'] = self.MakeValuesTopic(entityData)                    
                    autoDiscoverySendTopic = TOPIC_AUTODISCOVERY_FORMAT.format("switch",App.getName(),entityData.GetId().replace(".","_"))

                # Send
                self.client.SendTopicData(autoDiscoverySendTopic,json.dumps(payload))

            
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
        preset.AddEntry("Home assistant broker address",CONFIG_KEY_ADDRESS,mandatory=True)
        preset.AddEntry("Port",CONFIG_KEY_PORT,default=1883)
        preset.AddEntry("Client name",CONFIG_KEY_NAME,mandatory=True)
        preset.AddEntry("Username",CONFIG_KEY_USERNAME,default="")
        preset.AddEntry("Password",CONFIG_KEY_PASSWORD,default="")
        return preset