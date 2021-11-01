from Entities.Entity import Entity

# Linux dep
try:
    import os, re, sys
    from subprocess import PIPE, Popen
    linux_support=True
except:
    linux_support=False


# Windows dep
try:
    from win32gui import GetWindowText, GetForegroundWindow
    windows_support=True
except:
    windows_support=False

# macOS dep
try:
    from AppKit import NSWorkspace
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
    macos_support=True
except:
    macos_support=False


TOPIC = 'active_window'


class ActiveWindow(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def PostInitialize(self):
        os = self.GetOS()
        self.UpdateSpecificFunction = None   # Specific function for this os/de, set this here to avoid all if else except at each update

        if os == self.consts.FIXED_VALUE_OS_LINUX:
            if linux_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_Linux
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        elif os == self.consts.FIXED_VALUE_OS_WINDOWS:
            if windows_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_Windows
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        elif os == self.consts.FIXED_VALUE_OS_MACOS:
            if macos_support:
                self.UpdateSpecificFunction = self.GetActiveWindow_macOS
            else:
                raise Exception("Unsatisfied dependencies for this entity")
        else:
            raise Exception(
                'Entity not available for this operating system')

    def Update(self):
        self.SetTopicValue(TOPIC, str(self.UpdateSpecificFunction()))

    def GetActiveWindow_macOS(self):
        curr_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        curr_pid = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationProcessIdentifier']
        curr_app_name = curr_app.localizedName()
        options = kCGWindowListOptionOnScreenOnly
        windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
        for window in windowList:
            pid = window['kCGWindowOwnerPID']
            windowNumber = window['kCGWindowNumber']
            ownerName = window['kCGWindowOwnerName']
            geometry = window['kCGWindowBounds']
            windowTitle = window.get('kCGWindowName', u'Unknown')
            if curr_pid == pid:
                return windowTitle


    def GetActiveWindow_Windows(self):
        return GetWindowText(GetForegroundWindow())

    def GetActiveWindow_Linux(self):
        root = Popen( ['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout = PIPE )
        stdout, stderr = root.communicate()

        m = re.search( b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout )

        if m is not None:
            window_id = m.group( 1 )
            window = Popen( ['xprop', '-id', window_id, 'WM_NAME'], stdout = PIPE )
            stdout, stderr = window.communicate()

            match = re.match( b'WM_NAME\(\w+\) = (?P<name>.+)$', stdout )
            if match is not None:
                return match.group( 'name' ).decode( 'UTF-8' ).strip( '"' )

        return 'Inactive'

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()
