# Warehouse

## New Warehouse

Subclasses of "Warehouse" must have this functions

‘‘‘

@staticmethod
def InstantiateWithConfiguration(configuration):
    """ Receive a configuration and instantiate the warehouse with the correct ordered parameters """
    return 

@staticmethod
def ConfigurationPreset():
    """ Prepare a preset to manage settings insert/edit for the warehouse """
    return None

‘‘‘

These aren't in "Warehouse" because are static so would be unique in all Warehouses

Example present in HomeAssistantWarehouse

If not implmented:

- **InstantiateWithConfiguration** is replaced by the initializer of the class so the class will be initialized without a configuration
- **ConfigurationPreset** is not replaced: the menu will be blank and no configuration will be available for this warehouse