from Configurator.Configurator import MenuPreset
from Warehouse.Deployments.MQTTWarehouse.MQTTWarehouse import MQTTWarehouse

class HomeAssistantWarehouse(MQTTWarehouse):
    
    def Name(self):
        return "HomeAssistant"
    
    def InstantiateWithConfiguration(self,configuration):
        try:
            return MQTTWarehouse(configuration["address"], int(configuration["port"]),
                                configuration["name"], configuration["username"],
                                configuration["password"])
        except:
            raise Exception("Error while converting configuration to MQTTWarehouse")


    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Home assistant broker address","address",mandatory=True)
        preset.AddEntry("Port","port",default=1883)
        preset.AddEntry("Client name","name")
        preset.AddEntry("Username","username")
        preset.AddEntry("Password","password")
        return preset