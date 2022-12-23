import platform
import os
from IoTuring.Entity import consts


class Os():
    OS_NAME = platform.system()

    @staticmethod
    def GetOs() -> str:
        if Os.OS_NAME == 'Darwin':  # It's macOS
            return consts.OS_FIXED_VALUE_MACOS
        elif Os.OS_NAME == "Linux":
            return consts.OS_FIXED_VALUE_LINUX
        elif Os.OS_NAME == "Windows":
            return consts.OS_FIXED_VALUE_WINDOWS
        else:
            raise Exception(
                f"Operating system not in the fixed list. Please open a Git issue and warn about this: OS = {Os.OS_NAME}")

    @staticmethod
    def IsLinux() -> bool:
        return bool(Os.OS_NAME == 'Linux')
    
    @staticmethod
    def IsWindows() -> bool:
        return bool(Os.OS_NAME == 'Windows')

    @staticmethod
    def IsMacos() -> bool:
        return bool(Os.OS_NAME == 'Darwin')


class DesktopEnvironment():
    @staticmethod
    def GetDesktopEnvironment() -> str:            
        de = os.environ.get('DESKTOP_SESSION')
        if de == None:
            de = "base"
        return de
