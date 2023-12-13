import platform
import os
import psutil
import shutil

class OperatingSystemDetection():
    OS_NAME = platform.system()
    
    # Values to return as OS:
    MACOS = "macOS"
    WINDOWS = "Windows"
    LINUX = "Linux"

    # Values to use to detect the OS:
    MACOS_DETECTION_NAMES = ["macOS", "Darwin"]
    WINDOWS_DETECTION_NAMES = ["Windows"]
    LINUX_DETECTION_NAMES = ["Linux"]


    @classmethod
    def GetOs(cls) -> str:
        if cls.IsMacos():  
            return cls.MACOS
        elif cls.IsLinux():
            return cls.LINUX
        elif cls.IsWindows():
            return cls.WINDOWS
        else:
            raise Exception(
                f"Operating system not in the fixed list. Please open a Git issue and warn about this: OS = {cls.OS_NAME}")

    @classmethod
    def IsLinux(cls) -> bool:
        return bool(cls.OS_NAME in cls.LINUX_DETECTION_NAMES)
    
    @classmethod
    def IsWindows(cls) -> bool:
        return bool(cls.OS_NAME in cls.WINDOWS_DETECTION_NAMES)

    @classmethod
    def IsMacos(cls) -> bool:
        return bool(cls.OS_NAME in cls.MACOS_DETECTION_NAMES)

    @classmethod
    def GetEnv(cls, envvar) -> str:
        """Get envvar, also from different tty on linux"""
        env_value = os.environ.get(envvar) or ""
        if cls.IsLinux() and not env_value:
            try:
                # Try if there is another tty with gui:
                session_pid = next((u.pid for u in psutil.users() if u.host and "tty" in u.host), None) 
                if session_pid:
                    p = psutil.Process(int(session_pid))
                    with p.oneshot():
                        env_value = p.environ()[envvar]
            except KeyError:
                env_value = ""
        return env_value
            
    @staticmethod
    def CommandExists(command) -> bool:
        """Check if a command exists"""
        return bool(shutil.which(command))
