import os

class DesktopEnvironmentDetection():
    @staticmethod
    def GetDesktopEnvironment() -> str:            
        de = os.environ.get('DESKTOP_SESSION')
        if de == None:
            de = "base"
        return de
