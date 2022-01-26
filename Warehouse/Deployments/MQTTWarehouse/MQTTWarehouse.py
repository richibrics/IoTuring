from django.apps import AppConfig
from Configurator.MenuPreset import MenuPreset
from Protocols.MQTTClient.MQTTClient import MQTTClient
from Warehouse.Warehouse import Warehouse
from MyApp.App import App


TOPIC_FORMAT = "{}/{}/{}" # That stands for: App name, Client name, EntityData Id

class MQTTWarehouse(Warehouse):
    name = "MQTT"

    def __init__(self, address, port=1883, clientName=None, username=None, password=None) -> None:
        super().__init__()
        self.clientName = clientName
        self.client = MQTTClient(address, port, clientName, username, password)
        self.client.AsyncConnect()

    def Loop(self):
        # Here in Loop I send sensor's data (command callbacks are not managed here)
        for entity in self.GetEntities():
            for entitySensor in entity.GetEntitySensors():
                if(entitySensor.HasValue()):
                    self.client.SendTopicData(self.MakeTopic(entitySensor), entitySensor.GetValue())

    def MakeTopic(self,entityData):
        return MQTTClient.NormalizeTopic(TOPIC_FORMAT.format(App.getName(),self.clientName,entityData.GetId()))

    # CONFIGURATION

    @classmethod
    def InstantiateWithConfiguration(self, configuration: dict):
        try:
            return MQTTWarehouse(configuration["address"], int(configuration["port"]),
                                 configuration["name"], configuration["username"],
                                 configuration["password"])
        except Exception as e:
            raise Exception(
                "Error while converting configuration to MQTTWarehouse: " + str(e))

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Address", "address", mandatory=True)
        preset.AddEntry("Port", "port", default=1883)
        preset.AddEntry("Client name", "name", default=App.NAME)
        preset.AddEntry("Username", "username", default="")
        preset.AddEntry("Password", "password", default="")
        return preset
