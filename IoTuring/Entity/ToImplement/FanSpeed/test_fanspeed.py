import psutil
psutil.sensors_fans()

from IoTuring.Entity.ToImplement.FanSpeed.FanSpeeds import *

from IoTuring.Configurator.Configurator import  Configurator
configurator = Configurator()
config = configurator.GetConfigurations()
fan = Fanspeed(config)
fan.CallInitialize()

