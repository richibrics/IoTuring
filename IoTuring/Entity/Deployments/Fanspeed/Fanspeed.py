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
CONFIG_KEY_THRESHOLD = "threshold"

FANSPEED_DECIMALS = 0


class Fanspeed(Entity):
    """Entity to read fanspeed"""

    NAME = "Fanspeed"

    def Initialize(self) -> None:
        """Initialize the Class, setup Formatter, determin specificInitialize and specificUpdate depending on OS"""
        self.fanspeedFormatOptions = ValueFormatterOptions(
            value_type=ValueFormatterOptions.TYPE_ROTATION, decimals=FANSPEED_DECIMALS
        )

        self.specificInitialize = None
        self.specificUpdate = None

        if OsD.IsLinux():
            self.specificInitialize = self.InitLinux
            self.specificUpdate = self.UpdateLinux
        self.specificInitialize()

    def InitLinux(self) -> None:
        """OS dependant Init for Linux"""
        self.configuredPackages: list[str] = []
        self.registeredPackages: list[psutilFanspeedPackage] = []
        self.configuredThreshold: int 
        sensors = psutil.sensors_fans()
        self.Log(self.LOG_DEBUG, f"fancontrollers found:{sensors}")
        # load all controllers from config
        self.config = self.GetConfigurations()
        if self.config[CONFIG_KEY_THRESHOLD] is None:
            self.configuredThreshold = 200
            self.Log(self.LOG_DEBUG, "threshold is not configured setting it to 200rpm")
        self.configuredPackages.append(
            self.config[CONFIG_KEY_CONTROLLER]
        )  
        self.Log(self.LOG_DEBUG, f"registered controllers from config:{self.registeredPackages}")
        self.Log(self.LOG_DEBUG, f"got threshold as {self.configuredThreshold}rpm")
        for controllerName,data, in sensors.items():  # read the controllernames and fanspeeds
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

    def Update(self) -> None:
        """placeholder for OS specificUpdate"""
        self.specificUpdate()

    def UpdateLinux(self) -> None:
        """Updatemethod for Linux"""
        for package in self.registeredPackages:
            readout = psutil.sensors_fans()
            # Set main value = current fans above the configured threshold
            fanspeeds = []
            controller = package.packageName
            for i, fans in enumerate(package.attributes):
                fanspeeds.append(readout[controller][i].current)
            fans_above_threshold = self.above_threshold(fanspeeds, self.configuredThreshold)
            self.SetEntitySensorValue(package.packageName, fans_above_threshold)
            # Set extra attributes {fan name : fanspeed in rpm}
            for i, fan in enumerate(package.attributes):
                self.SetEntitySensorExtraAttribute(
                    package.packageName,
                    fan,
                    readout[package.packageName][i].current,
                    valueFormatterOptions=self.fanspeedFormatOptions,
                )

    def above_threshold(self, fans: list[int], threshold: int) -> int:
        above_threshold_fans = [num for num in fans if num > threshold]
        return len(above_threshold_fans)

    def prettyprint_controllers(controllers: dict) -> str:
        """print available controllers

        :param controllers: psutil.sensors_fans()
        :type controllers: dict
        :return: formated output as a string
        :rtype: str
        """
        output = "\n"
        indent = "\t"

        for controller in controllers.items():
            output += controller[0] + "\n"
            for fan in controller[1]:
                output += indent + fan[0] + " @ " + str(fan[1]) + "rpm\n"
        return output

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        """generate the preset for human input, prints the names of available fancontrollers in the terminal

        :return: preset
        :rtype: MenuPreset
        """
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
        preset.AddEntry(
            "At what threshold does a fan count as spinning [200]",
            CONFIG_KEY_THRESHOLD,
            mandatory=False
        )
        return preset


class psutilFanspeedPackage:
    """FanspeedPackage to pack all fans from a fancontroller"""

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
        return (
            self._sensors.copy()
        )  # Safe return: nobody outside can change the value !

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
        """attributes of the package, contain fans and their speeds

        :return: attributes
        :rtype: dict
        """
        for sensor in self.sensors:
            self._attributes[f"{sensor.label}"] = sensor.current
        return self._attributes


class psutilFanspeedSensor:
    """Sensor to pack fans of fancontrollers"""

    def __init__(self, sensorData) -> None:
        """sensorData is an element from the list which is the value of the the dict returned by psutil.sensors_fans()

        :param sensorData: list of sensorData[label, current]
        :type sensorData: list
        """
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
        """sensor label

        :return: packageName
        :rtype: str
        """
        return self._label
