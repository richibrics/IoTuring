from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity import consts

# Linux dep
try:
    import os
    import re
    import sys
    from subprocess import PIPE, Popen
    linux_support = True
except:
    linux_support = False


# Windows dep
try:
    from win32gui import GetWindowText, GetForegroundWindow
    windows_support = True
except:
    windows_support = False

# macOS dep (in PyObjC)
try:
    from AppKit import NSWorkspace
    macos_support = True
except:
    macos_support = False


KEY = 'active_window'


class ActiveWindow(Entity):
    NAME = "ActiveWindow"
    DEPENDENCIES = ["Os"]

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY))

    def PostInitialize(self):
        os = self.GetDependentEntitySensorValue("Os", "operating_system")
        # Specific function for this os/de, set this here to avoid all OS filters on Update
        self.UpdateSpecificFunction = None

        if os == consts.OS_FIXED_VALUE_LINUX:
            if linux_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_Linux
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        elif os == consts.OS_FIXED_VALUE_WINDOWS:
            if windows_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_Windows
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        elif os == consts.OS_FIXED_VALUE_MACOS:
            if macos_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_macOS
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        else:
            raise Exception(
                'Entity not available for this operating system')

    def Update(self):
        self.SetEntitySensorValue(KEY, str(self.UpdateSpecificFunction()))

    def GetActiveWindow_macOS(self):
        try:
            curr_app = NSWorkspace.sharedWorkspace().activeApplication()
            curr_app_name = curr_app['NSApplicationName']
            return curr_app_name  # Better choice beacuse on Mac the window title is a bit buggy
        except:
            return "Inactive"

    def GetActiveWindow_Windows(self):
        return GetWindowText(GetForegroundWindow())

    def GetActiveWindow_Linux(self):
        root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)
        stdout, stderr = root.communicate()

        m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)

        if m is not None:
            window_id = m.group(1)
            window = Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=PIPE)
            stdout, stderr = window.communicate()

            match = re.match(b'WM_NAME\(\w+\) = (?P<name>.+)$', stdout)
            if match is not None:
                return match.group('name').decode('UTF-8').strip('"')

        return 'Inactive'
