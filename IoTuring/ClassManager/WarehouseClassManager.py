from IoTuring.ClassManager.ClassManager import ClassManager
from IoTuring.ClassManager import consts


class WarehouseClassManager(ClassManager):
    """Class to load Warehouses from the Warehouses dir"""

    classesRelativePath = consts.WAREHOUSES_PATH
