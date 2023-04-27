from IoTuring.MyApp.SystemConsts.OperatingSystemDetection import OperatingSystemDetection as OsD


class DesktopEnvironmentDetection():
    @staticmethod
    def GetDesktopEnvironment() -> str:

        de = OsD.GetEnv('DESKTOP_SESSION')
        if not de:
            de = "base"
        return de

    @staticmethod
    def IsWayland() -> bool:
        return bool(
            OsD.GetEnv('WAYLAND_DISPLAY') or
            OsD.GetEnv('XDG_SESSION_TYPE') == 'wayland'
            )
