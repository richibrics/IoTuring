from IoTuring.ClassManager.ClassManager import ClassManager
from IoTuring.ClassManager import consts
from IoTuring.Entity.Entity import Entity


# Class to load Entities from the Entitties dir and get them from name
class EntityClassManager(ClassManager):
    def __init__(self):
        ClassManager.__init__(self)
        self.baseClass = Entity
        self.GetModulesFilename(consts.ENTITIES_PATH)
        # self.GetModulesFilename(consts.CUSTOM_ENTITIES_PATH) # TODO Decide if I'll use customs
