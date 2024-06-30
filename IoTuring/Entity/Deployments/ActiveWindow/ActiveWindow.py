import re
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De

import sys

# Windows dep
if OsD.IsWindows():
    from win32gui import GetWindowText, GetForegroundWindow

# macOS dep
if OsD.IsMacos():
    from AppKit import NSWorkspace


KEY = 'active_window'


class ActiveWindow(Entity):
    NAME = "ActiveWindow"

    def Initialize(self):

        UpdateFunction = {
            OsD.LINUX: self.GetActiveWindow_Linux,
            OsD.WINDOWS: self.GetActiveWindow_Windows,
            OsD.MACOS: self.GetActiveWindow_macOS
        }

        self.UpdateSpecificFunction = UpdateFunction[OsD.GetOs()]

        self.RegisterEntitySensor(EntitySensor(self, KEY))

    def Update(self):
        if self.UpdateSpecificFunction:
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

    def GetActiveWindow_Linux(self) -> str:
        p = self.RunCommand("xprop -root _NET_ACTIVE_WINDOW")

        if p.stdout:
            m = re.search('^_NET_ACTIVE_WINDOW.* ([\\w]+)$', p.stdout)

            if m is not None:
                window_id = m.group(1)

                if window_id == '0x0':
                    return 'Unknown'

                w = self.RunCommand(f"xprop -id {window_id} WM_NAME")

                if w.stderr:
                    return w.stderr

                match = re.match(
                    'WM_NAME\\(\\w+\\) = (?P<name>.+)$', w.stdout)

                if match is not None:
                    return match.group('name').strip('"')

        return 'Inactive'

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            if De.IsWayland():
                raise Exception("Wayland is not supported")
            elif not OsD.CommandExists("xprop"):
                raise Exception("No xprop command found!")

        elif OsD.IsWindows():
            if 'win32gui' not in sys.modules:
                raise Exception("Unsatisfied dependencies (win32gui) for this entity")

        elif OsD.IsMacos():
            if 'AppKit' not in sys.modules:
                raise Exception("Unsatisfied dependencies (AppKit) for this entity")
        else:
            raise cls.UnsupportedOsException()
