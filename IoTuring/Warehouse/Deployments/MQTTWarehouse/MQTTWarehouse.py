from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Protocols.MQTTClient.MQTTClient import MQTTClient
from IoTuring.Warehouse.Warehouse import Warehouse
from IoTuring.MyApp.App import App
from IoTuring.Entity.ValueFormat import ValueFormatter

import inspect  # To get this folder path
import os  # To get this folder path
import time


SLEEP_TIME_NOT_CONNECTED_WHILE = 1

TOPIC_FORMAT = "{}/{}/{}"  # That stands for: App name, Client name, EntityData Id

OUTPUT_TOPICS_FILENAME = "commands_topic.txt"

CONFIG_KEY_ADDRESS = "address"
CONFIG_KEY_PORT = "port"
CONFIG_KEY_NAME = "name"
CONFIG_KEY_USERNAME = "username"
CONFIG_KEY_PASSWORD = "password"
CONFIG_KEY_ADD_UNITS = "add_units"


class MQTTWarehouse(Warehouse):
    NAME = "MQTT"

    def Start(self):
        # I configure my Warehouse with configurations
        self.clientName = self.GetFromConfigurations(CONFIG_KEY_NAME)
        self.client = MQTTClient(self.GetFromConfigurations(CONFIG_KEY_ADDRESS),
                                 self.GetFromConfigurations(CONFIG_KEY_PORT),
                                 self.GetFromConfigurations(CONFIG_KEY_NAME),
                                 self.GetFromConfigurations(
                                     CONFIG_KEY_USERNAME),
                                 self.GetFromConfigurations(CONFIG_KEY_PASSWORD))
        self.addUnitsToValues = self.GetFromConfigurations(CONFIG_KEY_ADD_UNITS) # is a boolean
        self.client.AsyncConnect()
        self.RegisterEntityCommands()

        super().Start()  # Then run other inits (start the loop for example)

    def RegisterEntityCommands(self):
        """ Add EntityCommands to the MQTT client (subscribe to them) """
        for entity in self.GetEntities():
            for entityCommand in entity.GetEntityCommands():
                self.client.AddNewTopicToSubscribeTo(
                    self.MakeTopic(entityCommand), entityCommand.CallCallback)
                self.Log(self.LOG_DEBUG, entityCommand.GetId() +
                         " subscribed to " + self.MakeTopic(entityCommand))
        self.ExportCommandsTopics()

    def Loop(self):
        while(not self.client.IsConnected()):
            time.sleep(SLEEP_TIME_NOT_CONNECTED_WHILE)
            
        # Here in Loop I send sensor's data (command callbacks are not managed here)
        for entity in self.GetEntities():
            for entitySensor in entity.GetEntitySensors():
                if(entitySensor.HasValue()):
                    value = ValueFormatter.FormatValue(entitySensor.GetValue(), entitySensor.GetValueFormatterOptions(), self.addUnitsToValues)
                    self.client.SendTopicData(self.MakeTopic(
                        entitySensor), value)

    def MakeTopic(self, entityData):
        return MQTTClient.NormalizeTopic(TOPIC_FORMAT.format(App.getName(), self.clientName, entityData.GetId()))

    def ExportCommandsTopics(self):
        """ Create a file on which I write the Entity command Id and the topic """
        thisFolder = os.path.dirname(inspect.getfile(MQTTWarehouse))
        path = os.path.join(thisFolder, OUTPUT_TOPICS_FILENAME)
        with open(path, "w") as f:
            for entity in self.GetEntities():
                for entityCommand in entity.GetEntityCommands():
                    f.write(entityCommand.GetId() + " registered on " +
                            self.MakeTopic(entityCommand)+"\n")

    # CONFIGURATION
    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        preset.AddEntry("Address", CONFIG_KEY_ADDRESS, mandatory=True)
        preset.AddEntry("Port", CONFIG_KEY_PORT, default=1883)
        preset.AddEntry("Client name", CONFIG_KEY_NAME, default=App.getName())
        preset.AddEntry("Username", CONFIG_KEY_USERNAME, default="")
        preset.AddEntry("Password", CONFIG_KEY_PASSWORD, default="")
        preset.AddEntry("Add units to values (Y/N)", CONFIG_KEY_ADD_UNITS, default="Y", modify_value_callback=MenuPreset.Callback_NormalizeBoolean)
        return preset
