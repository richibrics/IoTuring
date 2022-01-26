from Configurator.MenuPreset import MenuPreset
from Warehouse.Deployments.MQTTWarehouse.MQTTWarehouse import MQTTWarehouse

class HomeAssistantWarehouse(MQTTWarehouse):

    def Name(self):
        return "HomeAssistant"
    
    @classmethod
    def InstantiateWithConfiguration(self,configuration):
        try:
            return MQTTWarehouse(configuration["address"], int(configuration["port"]),
                                configuration["name"], configuration["username"],
                                configuration["password"])
        except Exception as e:
            raise Exception("Error while converting configuration to HomeAssistantWarehouse: " + str(e))

    @classmethod
    def ConfigurationPreset(self):
        preset = MenuPreset()
        preset.AddEntry("Home assistant broker address","address",mandatory=True)
        preset.AddEntry("Port","port",default=1883)
        preset.AddEntry("Client name","name",mandatory=True)
        preset.AddEntry("Username","username",default="")
        preset.AddEntry("Password","password",default="")
        return preset