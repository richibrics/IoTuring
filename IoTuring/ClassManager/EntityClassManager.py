from IoTuring.ClassManager.ClassManager import ClassManager
from IoTuring.ClassManager import consts


# Class to load Entities from the Entitties dir
class EntityClassManager(ClassManager):
    classesRelativePath = consts.ENTITIES_PATH
