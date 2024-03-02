from IoTuring.ClassManager.ClassManager import ClassManager
from IoTuring.ClassManager import consts


class EntityClassManager(ClassManager):
    """Class to load Entities from the Entitties dir"""

    classesRelativePath = consts.ENTITIES_PATH
