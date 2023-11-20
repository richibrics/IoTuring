# Wireless strenght method taken from: https://github.com/s7jones/Wifi-Signal-Plotter/

import psutil


from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Configurator.MenuPreset import MenuPreset


supports_win_fanspeed = False
supports_linux_fanspeed = True
supports_macos_fanspeed = False

KEY_FANSPEED = "fanspeed"
KEY_FANLABEL = "fanlabel"

FALLBACK_PACKAGE_LABEL = "controller"
FALLBACK_SENSOR_LABEL = "fan"

CONFIG_KEY_CONTROLLER = "controller"

KEY_SENSOR_FORMAT = "{}"

FANSPEED_DECIMALS = 0


class Fanspeed(Entity):
    NAME = "Fanspeed"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.fanspeedFormatOptions = ValueFormatterOptions(
            value_type=ValueFormatterOptions.TYPE_ROTATION, decimals=FANSPEED_DECIMALS
        )

        self.specificInitialize = None
        self.specificUpdate = None

        if OsD.IsLinux():
            self.specificInitialize = self.InitLinux
            self.specificUpdate = self.UpdateLinux
        self.specificInitialize()

    def InitLinux(self):
        self.registeredPackages = []
        sensors = psutil.sensors_fans()
        self.Log(self.LOG_DEBUG, f"found fancontrollers:{sensors}")
        index = 1
        self.registeredPackages.append(self.GetConfigurations()[CONFIG_KEY_CONTROLLER])
        self.Log(self.LOG_DEBUG, f"registered controllers:{self.registeredPackages}")
        for pkgName, data in sensors.items():
            if pkgName in self.registeredPackages:
                package = psutilFanspeedPackage(pkgName, data)
                if package.hasCurrent():
                    self.registeredPackages.append(package.getLabel())
                    self.RegisterEntitySensor(
                        EntitySensor(
                            self,
                            self.packageNameToEntitySensorKey(package.getLabel()),
                            supportsExtraAttributes=True,
                            valueFormatterOptions=self.fanspeedFormatOptions,
                        )
                    )
            index += 1

    def Update(self):
        self.specificUpdate()

    def PostInitialize(self):
        os = self.GetOS()

        self.UpdateSpecificFunction = None  # Specific function for this os/de, set this here to avoid all if else except at each update

        if os == self.consts.FIXED_VALUE_OS_WINDOWS:
            self.UpdateSpecificFunction = self.GetCpuTemperature_Win
        # elif(Get_Operating_System() ==  self.consts.FIXED_VALUE_OS_MACOS):
        #    self.UpdateSpecificFunction = Get_Temperatures_macOS NOT SUPPORTED
        elif os == self.consts.FIXED_VALUE_OS_LINUX:
            self.UpdateSpecificFunction = self.UpdateLinux
        else:
            raise Exception("No temperature sensor available for this operating system")

    def UpdateLinux(self):
        # FanSpeed
        sensors = psutil.sensors_fans()
        index = 1
        for pkgName, data in sensors.items():
            if pkgName is None or pkgName == "":
                pkgName = FALLBACK_PACKAGE_LABEL.format(index)  # TODO
            package = psutilFanspeedPackage(pkgName, data)
            self.Log(self.LOG_DEBUG, f"trying to update {package.getLabel()}")
            if package.getLabel() in self.registeredPackages:
                self.Log(
                    self.LOG_DEBUG, f"{package.getLabel()} was in registeredPackages"
                )
                # Set main value = currently use amount of fans as entity state
                self.SetEntitySensorValue(
                    self.packageNameToEntitySensorKey(
                        # package.getLabel()), package.getCurrent()) # use some fanspeed as entity state
                        package.getLabel()
                    ),
                    len(package.getSensors()),
                )

                # Set extra attributes
                for key, value in package.getAttributesDict().items():
                    self.SetEntitySensorExtraAttribute(
                        self.packageNameToEntitySensorKey(package.getLabel()),
                        key,
                        value,
                        valueFormatterOptions=self.fanspeedFormatOptions,
                    )

            index += 1

    def packageNameToEntitySensorKey(self, packageName):
        return KEY_SENSOR_FORMAT.format(packageName)

    def prettyprint_controllers(controller_dict):
        output = "\n"
        indent = "\t"
        for controller in controller_dict.items():
            output += controller[0] + "\n"
            for fan in controller[1]:
                output += indent + fan[0] + " @ " + str(fan[1]) + "rpm\n"
        return output

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        controllers = psutil.sensors_fans()
        preset.AddEntry(
            "which controller to watch\ncontrollers:"
            + Fanspeed.prettyprint_controllers(controllers),
            CONFIG_KEY_CONTROLLER,
            mandatory=True,
        )
        return preset


class psutilFanspeedPackage:
    def __init__(self, packageName, packageData) -> None:
        """packageData is the value of the the dict returned by psutil.sensors_fans()"""
        self.packageName = packageName
        self.sensors = []
        for sensor in packageData:
            self.sensors.append(psutilFanspeedSensor(sensor))

    def getLabel(self) -> str:
        return self.packageName

    def getSensors(self) -> list:
        return self.sensors.copy()

    def getCurrent(self):
        """Returns highest current temperature among this package sensors. None if any sensor has that data."""
        for sensor in self.getSensors():
            return sensor.getCurrent()

    def hasCurrent(self):
        """True if at least a sensor of the package has the current property"""
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
                label = FALLBACK_SENSOR_LABEL.format(index)  # TODO
            if sensor.hasCurrent():
                attributes[f"{label} - Current"] = sensor.getCurrent()
        return attributes


class psutilFanspeedSensor:
    def __init__(self, sensorData) -> None:
        """sensorData is an element from the list which is the value of the the dict returned by psutil.sensors_fans()"""
        self.label = sensorData[0]
        self.current = sensorData[1]

    def getCurrent(self):
        return self.current

    def getLabel(self) -> str:
        return self.label

    def hasLabel(self):
        """True if a label is set for this sensor"""
        return not self.label is None and not self.label.strip() == ""

    def hasCurrent(self):
        """True if a current is set for this sensor"""
        return not self.current is None
