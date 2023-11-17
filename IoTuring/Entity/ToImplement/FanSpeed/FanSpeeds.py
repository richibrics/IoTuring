# Wireless strenght method taken from: https://github.com/s7jones/Wifi-Signal-Plotter/

import psutil
import re
import subprocess


from IoTuring.Entity.Entity import Entity 
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

supports_win_fanspeed = False
supports_linux_fanspeed = True 
supports_macos_fanspeed = False

KEY_FANSPEED = 'fanspeed'
KEY_FANLABEL = 'fanlabel'

KEY_SENSOR_FORMAT = "{}"

FANSPEED_DECIMALS = 0

class Fanspeed(Entity):
    NAME= "Fanspeed"
    def Initialize(self):
        self.fanspeedFormatOptions = ValueFormatterOptions(value_type=ValueFormatterOptions.TYPE_FANSPEED, decimals=FANSPEED_DECIMALS)

        self.specificInitialize = None
        self.specificUpdate= None

        if OsD.IsLinux():
            print("os is linux")
            self.specificInitialize = self.InitLinux
            self.specificUpdate = self.UpdateLinux
        self.specificInitialize()
        
    def InitLinux(self):
        print("initlinux")
        self.registeredPackages = []
        sensors = psutil.sensors_fans()
        index = 1
        print(sensors)
        for pkgName, data in sensors.items():

            if pkgName == None or pkgName == "":
                pkgName = FALLBACK_PACKAGE_LABEL.format(index) # TODO
            package = psutilFanspeedPackage(pkgName, data)
            if package.hasCurrent():
                self.registeredPackages.append(package.getLabel())
                self.RegisterEntitySensor(EntitySensor(
                    self, self.packageNameToEntitySensorKey(package.getLabel()), supportsExtraAttributes=True, valueFormatterOptions=self.fanspeedFormatOptions))
            index += 1
        
    def Update(self):
        self.specificUpdate()

    def PostInitialize(self):
        os = self.GetOS()
    
        self.UpdateSpecificFunction = None   # Specific function for this os/de, set this here to avoid all if else except at each update

        if(os == self.consts.FIXED_VALUE_OS_WINDOWS):
            self.UpdateSpecificFunction = self.GetCpuTemperature_Win
        # elif(Get_Operating_System() ==  self.consts.FIXED_VALUE_OS_MACOS):
        #    self.UpdateSpecificFunction = Get_Temperatures_macOS NOT SUPPORTED
        elif(os ==  self.consts.FIXED_VALUE_OS_LINUX):
            self.UpdateSpecificFunction = self.GetFanspeed_Unix
        else:
            raise Exception(
                'No temperature sensor available for this operating system')
        
    def UpdateLinux(self):
        # FanSpeed
        for controller in psutil.sensors_fans():
            self.SetEntitySensorValue(KEY_FANSPEED, psutil.sensors_fans())

    def packageNameToEntitySensorKey(self, packageName):
        return KEY_SENSOR_FORMAT.format(packageName)

    def GetFanspeed_Unix(self):
        fans = psutil.sensors_fans()
        if fans:
            for controller in fans:
                for fan in controller:
                    return fan.current
        else:
            self.Log(Logger.LOG_ERROR, "Can't get fanspeeds from your system.")
            self.Log(Logger.LOG_ERROR,
                     "Open a Git Issue and show this: " + str(fans))
            self.Log(Logger.LOG_ERROR, "Thank you")
            raise Exception("No dict data")
        raise Exception("No fanspeed data found")
                
    
    def GetCpuTemperature_Win(self):
        pass

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()

class psutilFanspeedPackage():
    def __init__(self, packageName, packageData) -> None:
        """ packageData is the value of the the dict returned by psutil.sensors_fans() """
        self.packageName = packageName
        self.sensors = []
        for sensor in packageData:
            self.sensors.append(psutilFanspeedSensor(sensor))

    def getLabel(self) -> str:
        return self.packageName

    def getSensors(self) -> list:
        return self.sensors.copy()

    def getCurrent(self):
        """ Returns highest current temperature among this package sensors. None if any sensor has that data. """
        highest = None
        for sensor in self.getSensors():
            if sensor.hasCurrent() and (highest == None or highest < sensor.getCurrent()):
                highest = sensor.getCurrent()
        return highest

    def hasCurrent(self):
        """ True if at least a sensor of the package has the current property """
        for sensor in self.sensors:
            if sensor.hasCurrent():
                return True
        return False

    def getAttributesDict(self):
        attributes = {}
        for index, sensor in enumerate(self.getSensors()):
            if sensor.hasLabel():
                label = sensor.getLabel()
            else:
                label = FALLBACK_SENSOR_LABEL.format(index)
            if sensor.hasCurrent():
                attributes[f"{label} - Current"] = sensor.getCurrent()
        return attributes

class psutilFanspeedSensor():
    def __init__(self, sensorData) -> None:
        """ sensorData is an element from the list which is the value of the the dict returned by psutil.sensors_temperatures() """
        self.label = sensorData[0]
        self.current = sensorData[1]

    def hasCurrent(self):
        """ True if a current is set for this sensor """
        return not self.current == None

    def hasLabel(self):
        """ True if a label is set for this sensor """
        return not self.label == None and not self.label.strip() == ""

    def getCurrent(self):
        return self.current

    def getLabel(self) -> str:
        return self.label