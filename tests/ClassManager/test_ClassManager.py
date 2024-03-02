from IoTuring.ClassManager.ClassManager import ClassManager, KEY_ENTITY, KEY_WAREHOUSE


class TestClassManager:
    def testClassCount(self):
        for class_key in [KEY_ENTITY, KEY_WAREHOUSE]:

            cm = ClassManager(class_key)
            assert bool(cm.loadedClasses) == False

            class_num = len(cm.ListAvailableClasses())
            assert class_num == len(cm.GetModuleFilePaths())
            assert class_num == len(cm.loadedClasses)
