import platform
import os
from IoTuring.MyApp.SystemConsts import consts

class OperatingSystemDetection():
    OS_NAME = platform.system()
    
    from .consts import OS_FIXED_VALUE_LINUX, OS_FIXED_VALUE_MACOS, OS_FIXED_VALUE_WINDOWS

    @staticmethod
    def GetOs() -> str:
        if OperatingSystemDetection.IsMacos():  
            return OperatingSystemDetection.OS_FIXED_VALUE_MACOS
        elif OperatingSystemDetection.IsLinux():
            return OperatingSystemDetection.OS_FIXED_VALUE_LINUX
        elif OperatingSystemDetection.IsWindows():
            return OperatingSystemDetection.OS_FIXED_VALUE_WINDOWS
        else:
            raise Exception(
                f"Operating system not in the fixed list. Please open a Git issue and warn about this: OS = {OperatingSystemDetection.OS_NAME}")

    @staticmethod
    def IsLinux() -> bool:
        return bool(OperatingSystemDetection.OS_NAME == 'Linux')
    
    @staticmethod
    def IsWindows() -> bool:
        return bool(OperatingSystemDetection.OS_NAME == 'Windows')

    @staticmethod
    def IsMacos() -> bool:
        return bool(OperatingSystemDetection.OS_NAME == 'Darwin') # It's macOS