from django.apps import AppConfig
from Configurator.Configurator import MenuPreset
from Protocols.MQTTClient.MQTTClient import MQTTClient
from Warehouse.Warehouse import Warehouse
from App.App import App

class MQTTWarehouse(Warehouse):
    client = None

    def __init__(self, address, port=1883, name=None, username=None, password=None) -> None:
        super().__init__()
        client = MQTTClient(address, port, name, username, password)
    
    def Name(self):
        return "MQTT"
    
    @classmethod
    def InstantiateWithConfiguration(self,configuration: dict):
        try:
            return MQTTWarehouse(configuration["address"], int(configuration["port"]),
                                configuration["name"], configuration["username"],
                                configuration["password"])
        except Exception as e:
            raise Exception("Error while converting configuration to MQTTWarehouse: " + str(e))

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Address","address",mandatory=True)
        preset.AddEntry("Port","port",default=1883)
        preset.AddEntry("Client name","name",default=App.NAME)
        preset.AddEntry("Username","username",default="")
        preset.AddEntry("Password","password",default="")
        return preset