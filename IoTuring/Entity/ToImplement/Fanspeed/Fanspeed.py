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

#KEY_SENSOR_FORMAT = "{}"

FANSPEED_DECIMALS = 0


class Fanspeed(Entity):
    NAME = "Fanspeed"

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
        self.configuredPackages: list[str] = []
        self.registeredPackages: list[psutilFanspeedPackage] = [] 
        sensors = psutil.sensors_fans()
        self.Log(self.LOG_DEBUG, f"found fancontrollers:{sensors}")
        self.configuredPackages.append(self.GetConfigurations()[CONFIG_KEY_CONTROLLER]) # load all controllers from config
        self.Log(self.LOG_DEBUG, f"registered controllers from config:{self.registeredPackages}")
        for controllerName, data in sensors.items(): # read the controllernames and fanspeeds 
            # build packages from controllernames if they are in the config
            if controllerName in self.configuredPackages:
                package = psutilFanspeedPackage(controllerName, data) 
                # register the entity and give it an initial value
                if package.hasCurrent():
                    # build the list of FanspeedPackage objects and register them as Entitys
                    self.registeredPackages.append(package)
                    self.RegisterEntitySensor(
                        EntitySensor(
                            self,
                            package.packageName,
                            supportsExtraAttributes=True,
                            valueFormatterOptions=self.fanspeedFormatOptions,
                        )
                    )

    def Update(self):
        self.specificUpdate()

    def UpdateLinux(self):
        # FanSpeed
        readout = psutil.sensors_fans()
        for package in self.registeredPackages:
            self.SetEntitySensorValue(package.packageName, len(package.sensors))
            self.Log(
                self.LOG_DEBUG, f"{package.packageName} was in registeredPackages"
            )
            # Set main value = currently use amount of fans as entity state
            self.SetEntitySensorValue(package.packageName, len(package.sensors))

            # Set extra attributes
            for fan in package.attributes:
                self.SetEntitySensorExtraAttribute(
                    package.packageName,
                    fan,
                    package.attributes[fan],
                    valueFormatterOptions=self.fanspeedFormatOptions,
                )

    def prettyprint_controllers(controllers: dict):
        output = "\n"
        indent = "\t"
        
        for controller in controllers.items():
            output += controller[0] + "\n"
            for fan in controller[1]:
                output += indent + fan[0] + " @ " + str(fan[1]) + "rpm\n"
        return output

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        controllers = psutil.sensors_fans()
        controllerNames = []
        for name in controllers:
            controllerNames.append(name)
        preset.AddEntry(
            f"which controller to watch\ncontrollers: {controllerNames}"
            + Fanspeed.prettyprint_controllers(controllers),
            CONFIG_KEY_CONTROLLER,
            mandatory=True,
        )
        return preset


class psutilFanspeedPackage:
    """FanspeedPackage to pack all fans from a fancontroller
    """
    def __init__(self, packageName: str, packageData: int) -> None:
        """packageData is the value of the the dict returned by psutil.sensors_fans()

        :param packageName: name of the fanspeedController
        :type packageName: str
        :param packageData: fanspeed
        :type packageData: int
        """
        self._packageName = packageName
        self._sensors: list[psutilFanspeedSensor] = []
        self._attributes = {}
        for sensor in packageData:
            self._sensors.append(psutilFanspeedSensor(sensor))

    @property
    def packageName(self) -> str:
        """packageName property

        :return: packageName
        :rtype: str
        """
        return self._packageName

    @property
    def sensors(self) -> list:
        """sensors property

        :return: list of fanspeedsensors from a fancontroller
        :rtype: list
        """
        return self._sensors.copy() # Safe return: nobody outside can change the value !

    @property
    def highest(self):
        """highest property

        :return: highest current fanspeed among this package sensors
        :rtype: int
        """
        if self.hasCurrent():
            speeds: int = self.attributes
            return max(speeds)
        return False

    def hasCurrent(self):
        """True if at least a sensor of the package has the current property

        :return: if one sensor has a current speed
        :rtype: bool
        """
        if any(self.attributes):
            return True
        return False

    @property
    def attributes(self):
        for sensor in self.sensors:
                self._attributes[f"{sensor.label}"] = sensor.current
        return self._attributes


class psutilFanspeedSensor:
    def __init__(self, sensorData) -> None:
        """sensorData is an element from the list which is the value of the the dict returned by psutil.sensors_fans()"""
        self._label = sensorData[0]
        self._current = sensorData[1]

    @property
    def current(self) -> int:
        """current fanspeed getter

        :return: current
        :rtype: int
        """
        return self._current

    @property
    def label(self) -> str:
        """packageName getter

        :return: packageName
        :rtype: str
        """
        return self._label
