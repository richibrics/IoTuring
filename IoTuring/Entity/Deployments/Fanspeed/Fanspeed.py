import psutil

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Configurator.MenuPreset import MenuPreset


supports_win_fanspeed = False
supports_linux_fanspeed = True
supports_macos_fanspeed = True

KEY_FANSPEED = "fanspeed"
KEY_FANLABEL = "fanlabel"

FALLBACK_PACKAGE_LABEL = "controller"
FALLBACK_SENSOR_LABEL = "fan"

CONFIG_KEY_CONTROLLER = "controller"
CONFIG_KEY_THRESHOLD = "threshold"

FANSPEED_DECIMALS = 0

FANSPEED_CHOICE_STRING = "{}:\n with fans: {}"


class Fanspeed(Entity):
    """Entity to read fanspeed"""

    NAME = "Fanspeed"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self) -> None:
        """Initialize the Class, setup Formatter, determin specificInitialize and specificUpdate depending on OS"""
        self.fanspeedFormatOptions = ValueFormatterOptions(
            value_type=ValueFormatterOptions.TYPE_ROTATION, decimals=FANSPEED_DECIMALS
        )

        self.specificInitialize = None
        self.specificUpdate = None

        if OsD.IsLinux() or OsD.IsMacos():
            if not hasattr(psutil, "sensors_fans"):
                raise Exception("No fan found in system")
            self.specificInitialize = self.InitUnix
            self.specificUpdate = self.UpdateLinux
        elif OsD.IsWindows():
            raise NotImplementedError
            
        self.specificInitialize()

    def InitUnix(self) -> None:
        """OS dependant Init for Unix systems"""
        self.configuredPackages: list[str] = []
        self.registeredPackages: list[psutilFanspeedPackage] = []
        self.configuredThreshold: int 
        sensors = psutil.sensors_fans()
        self.Log(self.LOG_DEBUG, f"fancontrollers found:{sensors}")
        # load all controllers from config
        self.config = self.GetConfigurations()
        self.configuredThreshold = self.config[CONFIG_KEY_THRESHOLD]
        if isinstance(self.configuredThreshold, str): # convert to int from configuration string
            self.configuredThreshold = int(self.configuredThreshold)
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
                            valueFormatterOptions=None, # give the state no unit since it resembles num of fans spinning above threshold
                        )
                    )

    def Update(self) -> None:
        """placeholder for OS specificUpdate"""
        self.specificUpdate()

    def UpdateLinux(self) -> None:
        """Updatemethod for Linux"""
        for package in self.registeredPackages:
            readout = psutil.sensors_fans()
            # Set main value = gitcurrent fans above the configured threshold
            fanspeeds = [fan.current for fan in readout[package.packageName]]
            # find fans above threshold and assign the entity state
            self.SetEntitySensorValue(package.packageName, self.above_threshold(fanspeeds, self.configuredThreshold))
            # Set extra attributes {fan name : fanspeed in rpm}
            for label, current in package.attributes.items():
                self.SetEntitySensorExtraAttribute(
                    package.packageName,
                    label,
                    current,
                    valueFormatterOptions=self.fanspeedFormatOptions,
                )

    @staticmethod
    def above_threshold(fanspeeds: list[int], threshold: int) -> int:
        """filters a list of integers for values above a threshold returns amount of values above threshold

        :param fanspeeds: list of fanspeeds
        :type fans: list[int]
        :param threshold: threshold to filter values below
        :type threshold: int
        :return: amount of fanspeeds above threshold
        :rtype: int
        """
        above_threshold_fans = [num for num in fanspeeds if num > threshold]
        return len(above_threshold_fans)


    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        """generate the preset for human input, prints the names of available fancontrollers in the terminal

        :return: preset 
        :rtype: MenuPreset
        """

        FAN_CHOICES = []
        
        for controller, fans in psutil.sensors_fans().items():
            fanList = []
            for fan in fans:
                fanList.append(f"{fan.label}@{fan.current}rpm")
            FAN_CHOICES.append({
                "name": FANSPEED_CHOICE_STRING.format(controller, ", ".join(fanList)),
                "value": controller
                }                
            )

        preset = MenuPreset()
        preset.AddEntry(
            name="controllers to check",
            key=CONFIG_KEY_CONTROLLER,
            mandatory=True,
            question_type="select",
            choices=FAN_CHOICES
        )
        preset.AddEntry(
            name="At what threshold does a fan count as spinning",
            key=CONFIG_KEY_THRESHOLD,
            default="200",
            mandatory=False
        )
        return preset


class psutilFanspeedPackage():
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
        for sensor in self._sensors:
            self._attributes[f"{sensor.label}"] = sensor.current
        return self._attributes


class psutilFanspeedSensor():
    """Sensor to pack fans of fancontrollers"""

    def __init__(self, sensorData: psutil._common.sfan) -> None:
        """sensorData is an element from the list which is the value of the the dict returned by psutil.sensors_fans()

        :param sensorData: list of sensorData[label, current]
        :type sensorData: list
        """
        if sensorData.label == '':
            self._label = FALLBACK_SENSOR_LABEL
        else: 
            self._label = sensorData.label
        if sensorData.current == '':
            raise Exception("fanspeed is not reported")
        else:
            self._current = sensorData.current

    @property
    def current(self) -> int:
        """current fanspeed

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
