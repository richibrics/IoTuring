import subprocess
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

    @staticmethod
    def CheckXsetSupport() -> None:
        """ Check if system supports xset. Raises exception if not supported """
        if not OsD.CommandExists("xset"):
            raise Exception("xset command not found!")
        else:
            # Check if xset is working:
            p = subprocess.run(['xset', 'dpms'], capture_output=True, shell=False)
            if p.stderr:
                raise Exception(f"Xset dpms error: {p.stderr.decode()}")
            elif not OsD.GetEnv('DISPLAY'):
                raise Exception('No $DISPLAY environment variable!')

        