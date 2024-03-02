from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager


class TestEntityClassManager:
    def testClassCount(self):
        ecm = EntityClassManager()
        assert bool(ecm.loadedClasses) == False
        
        class_num = len(ecm.ListAvailableClasses())
        assert class_num == len(ecm.GetModuleFilePaths())
        assert class_num == len(ecm.loadedClasses)


class TestWarehouseClassManager:
    def testClassCount(self):
        wcm = WarehouseClassManager()
        assert bool(wcm.loadedClasses) == False
        
        class_num = len(wcm.ListAvailableClasses())
        assert class_num == len(wcm.GetModuleFilePaths())
        assert class_num == len(wcm.loadedClasses)
