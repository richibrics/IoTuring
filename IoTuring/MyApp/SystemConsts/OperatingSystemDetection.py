import platform
import os
import psutil
import shutil
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

    @staticmethod
    def GetEnv(envvar) -> str:
        """Get envvar, also from different tty on linux"""
        env_value = ""
        if OperatingSystemDetection.IsLinux():
            e = os.environ.get(envvar)
            if not e:
                try:
                    # Try if there is another tty with gui:
                    session_pid = next((u.pid for u in psutil.users() if u.host and "tty" in u.host), None) 
                    if session_pid:
                        p = psutil.Process(int(session_pid))
                        with p.oneshot():
                            env_value = p.environ()[envvar]
                except KeyError:
                    env_value = ""
            else:
                env_value = e

        return env_value
            
    @staticmethod
    def CommandExists(command) -> bool:
        """Check if a command exists"""
        return bool(shutil.which(command))
