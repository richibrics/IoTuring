from IoTuring.Configurator.MenuPreset import MenuPreset


class ConfiguratorObject:
    """ Base class for configurable classes """

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        """ Prepare a preset to manage settings insert/edit for the warehouse or entity """
        return MenuPreset()
