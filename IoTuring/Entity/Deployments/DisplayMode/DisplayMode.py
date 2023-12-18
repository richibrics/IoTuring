import os as sys_os
from IoTuring.Entity.Entity import Entity
from ctypes import *
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

from IoTuring.Entity.EntityData import EntityCommand

SELECT_INTERNAL_MONITOR = "Only internal display"
SELECT_EXTERNAL_MONITOR = "Only external display"
SELECT_EXTEND_MONITOR = "Extend displays"
SELECT_CLONE_MONITOR = "Clone displays"
KEY_MODE = "mode"

class DisplayMode(Entity):
    NAME = "DisplayMode"

    def Initialize(self):
        callback = None
        if OsD.IsWindows():
            sr = OsD.GetEnv('SystemRoot')
            if sys_os.path.exists(r'{}\System32\DisplaySwitch.exe'.format(sr)):
                callback = self.Callback_Win
            else:
                self.Log(self.LOG_ERROR, "Error log:\nOperating system: {}, sr: {}, path exists: {}".format(OsD.GetOs(), sr, sys_os.path.exists('{}\System32\DisplaySwitch.exe'.format(sr))))
                raise Exception("Unsupported software, report this log to the developer")
        else:
            raise Exception("Unsupported operating system for this entity")
            
        self.RegisterEntityCommand(EntityCommand(
            self, KEY_MODE, callback))

    def Callback_Win(self, message):
        parse_select_command = {SELECT_INTERNAL_MONITOR: "internal",
                     SELECT_EXTERNAL_MONITOR: "external",
                     SELECT_CLONE_MONITOR: "clone",
                     SELECT_EXTEND_MONITOR: "extend"}   
                         
        if message.payload.decode('utf-8') not in parse_select_command:
            self.Log(self.LOG_WARNING, f"Invalid command: {message.payload.decode('utf-8')}")
        else:
            sr = OsD.GetEnv('SystemRoot')
            command = r'{}\System32\DisplaySwitch.exe /{}'.format(sr, parse_select_command[message.payload.decode('utf-8')])
            self.RunCommand(command=command)

