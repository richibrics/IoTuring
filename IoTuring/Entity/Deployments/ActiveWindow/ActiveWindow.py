from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De


# Linux dep
try:
    import re
    from subprocess import PIPE, Popen
    linux_support = True
except BaseException:
    linux_support = False


# Windows dep
try:
    from win32gui import GetWindowText, GetForegroundWindow
    windows_support = True
except BaseException:
    windows_support = False

# macOS dep
try:
    from AppKit import NSWorkspace
    macos_support = True
except BaseException:
    macos_support = False

KEY = 'active_window'


class ActiveWindow(Entity):
    NAME = "ActiveWindow"

    def Initialize(self):

        # Specific function for this os/de, set this here to avoid all OS
        # filters on Update
        self.UpdateSpecificFunction = None

        if OsD.IsLinux():
            if De.IsWayland():
                raise Exception("Wayland is not supported")
            elif linux_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_Linux
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        elif OsD.IsWindows():
            if windows_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_Windows
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        elif OsD.IsMacos():
            if macos_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_macOS
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        else:
            raise Exception(
                'Entity not available for this operating system')

        if self.UpdateSpecificFunction:
            self.RegisterEntitySensor(EntitySensor(self, KEY))

    def Update(self):
        self.SetEntitySensorValue(KEY, str(self.UpdateSpecificFunction()))

    def GetActiveWindow_macOS(self):
        try:
            curr_app = NSWorkspace.sharedWorkspace().activeApplication()
            curr_app_name = curr_app['NSApplicationName']
            return curr_app_name  # Better choice beacuse on Mac the window title is a bit buggy
        except BaseException:
            return "Inactive"

    def GetActiveWindow_Windows(self):
        return GetWindowText(GetForegroundWindow())

    def GetActiveWindow_Linux(self):
        root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)
        stdout, stderr = root.communicate()

        m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\\w]+)$', stdout)

        if m is not None:
            window_id = m.group(1)
            window = Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=PIPE)
            stdout, stderr = window.communicate()

            match = re.match(b'WM_NAME\\(\\w+\\) = (?P<name>.+)$', stdout)
            if match is not None:
                return match.group('name').decode('UTF-8').strip('"')

        return 'Inactive'
