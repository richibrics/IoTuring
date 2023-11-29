import platform
import os
import psutil
import shutil

class OperatingSystemDetection():
    OS_NAME = platform.system()
    
    # Fixed list:
    MACOS = "macOS"
    WINDOWS = "Windows"
    LINUX = "Linux"


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
        return bool(cls.OS_NAME == cls.LINUX)
    
    @classmethod
    def IsWindows(cls) -> bool:
        return bool(cls.OS_NAME == cls.WINDOWS)

    @classmethod
    def IsMacos(cls) -> bool:
        return bool(cls.OS_NAME == cls.MACOS)

    @classmethod
    def GetEnv(cls, envvar) -> str:
        """Get envvar, also from different tty on linux"""
        env_value = ""
        if cls.IsLinux():
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
