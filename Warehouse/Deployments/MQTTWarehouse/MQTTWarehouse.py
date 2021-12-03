from Configurator.Configurator import MenuPreset
from Protocols.MQTTClient.MQTTClient import MQTTClient
from Warehouse.Warehouse import Warehouse


class MQTTWarehouse(Warehouse):
    client = None

    def __init__(self, address, port=1883, name=None, username=None, password=None) -> None:
        super().__init__()
        client = MQTTClient(address, port, name, username, password)
    
    def Name(self):
        return "MQTT"
    
    def InstantiateWithConfiguration(self,configuration):
        try:
            return MQTTWarehouse(configuration["address"], int(configuration["port"]),
                                configuration["name"], configuration["username"],
                                configuration["password"])
        except:
            raise Exception("Error while converting configuration to MQTTWarehouse")

    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Address","address",mandatory=True)
        preset.AddEntry("Port","port",default=1883)
        preset.AddEntry("Client name","name")
        preset.AddEntry("Username","username")
        preset.AddEntry("Password","password")
        return preset