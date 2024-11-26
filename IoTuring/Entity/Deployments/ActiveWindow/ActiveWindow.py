import re
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import DesktopEnvironmentDetection as De


# Windows dep
try:
    from win32gui import GetWindowText, GetForegroundWindow  # type: ignore
    windows_support = True
except BaseException:
    windows_support = False

# macOS dep
try:
    from AppKit import NSWorkspace  # type: ignore
    macos_support = True
except BaseException:
    macos_support = False

KEY = 'active_window'


class ActiveWindow(Entity):
    NAME = "ActiveWindow"

    def Initialize(self):

        UpdateFunction = {
            OsD.LINUX: self.GetActiveWindow_Linux,
            OsD.WINDOWS: self.GetActiveWindow_Windows,
            OsD.MACOS: self.GetActiveWindow_macOS,
            'hyprland': self.GetActiveWindow_Hyprland,      # each Wayland compositor need its own implementation since they have their own apis
        }

        self.UpdateSpecificFunction = UpdateFunction[OsD.GetOs()]
        if De.GetDesktopEnvironment() == 'hyprland':
            self.UpdateSpecificFunction = UpdateFunction['hyprland']
            self.hyprland_regex_patterns = {
                'workspace': r'workspace:\s*(\d+)',
                'floating': r'floating:\s*(\d+)',
                'monitor': r'monitor:\s*(\d+)',
                'class': r'class:\s*(\S+)',
                'title': r'title:\s*(.*)',
                'initialTitle': r'initialTitle:\s*"(.+?)"',
                'pid': r'pid:\s*(\d+)',
                'xwayland': r'xwayland:\s*(\d+)',
                'fullscreen': r'fullscreen:\s*(\d+)',
                'pinned': r'pinned:\s*(\d+)'
            } 
        self.RegisterEntitySensor(EntitySensor(self, KEY, supportsExtraAttributes=True))

        self.extraAttributes = {}

    def Update(self):
        if self.UpdateSpecificFunction:
            self.SetEntitySensorValue(KEY, str(self.UpdateSpecificFunction()))
            if self.extraAttributes:
                for extraAttributeKey, extraAttributeValue in self.extraAttributes.items():
                    self.SetEntitySensorExtraAttribute(KEY, extraAttributeKey, extraAttributeValue)

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

    def GetActiveWindow_Hyprland(self):
        title = None
        p = self.RunCommand('hyprctl activewindow')
        # if the command was successful, assign all lines to respective variables
        if p.stdout:
            # Use regular expressions to search for each variable in the output
            for key, pattern in self.hyprland_regex_patterns.items():
                match = re.search(pattern, p.stdout)
                if match:
                    if key == 'title':
                        title = match.group(1)
                    self.extraAttributes[key] = match.group(1)


            return title


    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            if De.IsWayland():
                if De.GetDesktopEnvironment() == 'hyprland':
                    if not OsD.CommandExists("hyprctl"):
                        raise Exception("No hyprctl command found!")
                else:
                    raise Exception("Wayland is not supported")
            elif not OsD.CommandExists("xprop"):
                raise Exception("No xprop command found!")

        elif OsD.IsWindows() or OsD.IsMacos():

            if (OsD.IsWindows() and not windows_support) or\
                    (OsD.IsMacos() and not macos_support):
                raise Exception("Unsatisfied dependencies for this entity")

        else:
            raise cls.UnsupportedOsException()
