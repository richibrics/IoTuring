import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD # don't name Os as could be a problem with old configurations that used the Os entity

KEY_SENSOR_FORMAT = "{}"
FALLBACK_PACKAGE_LABEL = "package_{}"
FALLBACK_SENSOR_LABEL = "sensor_{}"
TEMPERATURE_DECIMALS = 1

INVALID_SMC_VALUE_HIGH = 120 # skip sensors if when initialized they return a value higher than this
MACOS_SMC_TEMPERATURE_KEYS = {
    "CPU core A": "TC0c",
    "CPU core B": "TC1c",
    "CPU core C": "TC2c",
    "CPU core D": "TC3c",
    "CPU core E": "TC4c",
    "CPU core F": "TC5c",
    "CPU core G": "TC6c",
    "CPU core H": "TC7c",
    "CPU core I": "TC8c",
    "CPU core J": "TC9c",
    "CPU performance core 1 temperature": "Tp01", # ARM
    "CPU performance core 2 temperature": "Tp05", # ARM
    "CPU performance core 3 temperature": "Tp0D", # ARM
    "CPU performance core 4 temperature": "Tp0H", # ARM
    "CPU performance core 5 temperature": "Tp0L", # ARM
    "CPU performance core 6 temperature": "Tp0P", # ARM
    "CPU performance core 7 temperature": "Tp0X", # ARM
    "CPU performance core 8 temperature": "Tp0b", # ARM
    "CPU efficient core 1 temperature": "Tp09", # ARM
    "CPU efficient core 2 temperature": "Tp0T" # ARM
}

class Temperature(Entity):
    NAME = "Temperature"

    def Initialize(self):
        self.temperatureFormatOptions = ValueFormatterOptions(value_type=ValueFormatterOptions.TYPE_TEMPERATURE, decimals=TEMPERATURE_DECIMALS)

        self.specificInitialize = None
        self.specificUpdate = None
        
        if OsD.IsLinux():
            self.specificInitialize = self.InitLinux
            self.specificUpdate = self.UpdateLinux
        elif OsD.IsMacos():
            self.specificInitialize = self.InitmacOS
            self.specificUpdate = self.UpdatemacOS
        else:
            raise Exception("Unsupported operating system.")
        self.specificInitialize()

    def Update(self):
        self.specificUpdate()
        
    def InitmacOS(self):
        import ioturing_applesmc
        self.RegisterEntitySensor(EntitySensor(self, "cpu", supportsExtraAttributes=True, valueFormatterOptions=self.temperatureFormatOptions))
        self.valid_keys = []
        # get smc values for all the keys I have in the dictionary and remember
        # the keys that do not return a 0.0 value
        ioturing_applesmc.open_smc()
        for key, value in MACOS_SMC_TEMPERATURE_KEYS.items():
            smc_value = ioturing_applesmc.get_temperature(value)
            if smc_value != 0.0 and smc_value < INVALID_SMC_VALUE_HIGH:
                self.valid_keys.append(value)
        if len(self.valid_keys) == 0:
            raise Exception("No valid sensor found for cpu temperature.")
        
    # get smc values for all valid keys previously found, then set the sensor value 
    # to the highest value found. Save also the other values in the extra attributes.
    def UpdatemacOS(self):
        import ioturing_applesmc
        values = {}
        # key = description, value = smc key
        for key, value in MACOS_SMC_TEMPERATURE_KEYS.items():
            if value in self.valid_keys: # in valid_keys I have only the smc keys that returned a value != 0.0
                values[key] = ioturing_applesmc.get_temperature(value)
        
        # Set main value to the highest value found
        self.SetEntitySensorValue("cpu", max(values.values()))
        # Set extra attributes
        for key, value in values.items():
            self.SetEntitySensorExtraAttribute("cpu", key, values[key], valueFormatterOptions=self.temperatureFormatOptions)
        
    # I don't register packages that do not have Current temperature, so I store the registered in a list which is then checked during update
    def InitLinux(self):
        self.registeredPackages = []
        sensors = psutil.sensors_temperatures()
        index = 1
        for pkgName, data in sensors.items():
            if pkgName == None or pkgName == "":
                pkgName = FALLBACK_PACKAGE_LABEL.format(index)
            package = psutilTemperaturePackage(pkgName, data)
            if package.hasCurrent():
                self.registeredPackages.append(package.getLabel())
                self.RegisterEntitySensor(EntitySensor(
                    self, self.packageNameToEntitySensorKey(package.getLabel()), supportsExtraAttributes=True, valueFormatterOptions=self.temperatureFormatOptions))
            index += 1
            
    def UpdateLinux(self):
        sensors = psutil.sensors_temperatures()
        index = 1
        for pkgName, data in sensors.items():
            if pkgName == None or pkgName == "":
                pkgName = FALLBACK_PACKAGE_LABEL.format(index)
            package = psutilTemperaturePackage(pkgName, data)
            if package.getLabel() in self.registeredPackages:
                # Set main value = current of the package
                self.SetEntitySensorValue(self.packageNameToEntitySensorKey(
                    package.getLabel()), package.getCurrent())
                
                # Set extra attributes
                for key, value in package.getAttributesDict().items():
                    self.SetEntitySensorExtraAttribute(self.packageNameToEntitySensorKey(
                        package.getLabel()), key, value, valueFormatterOptions=self.temperatureFormatOptions)
                    
            index += 1

    def packageNameToEntitySensorKey(self, packageName):
        return KEY_SENSOR_FORMAT.format(packageName)


class psutilTemperaturePackage():
    def __init__(self, packageName, packageData) -> None:
        """ packageData is the value of the the dict returned by psutil.sensors_temperatures() """
        self.packageName = packageName
        self.sensors = []
        for sensor in packageData:
            self.sensors.append(psutilTemperatureSensor(sensor))

    def getLabel(self) -> str:
        return self.packageName

    def getSensors(self) -> list:
        return self.sensors.copy()

    # Package stats strategies here: my choice is to return always the highest among the temperatures, critical: here will return the lowest
    def getCurrent(self):
        """ Returns highest current temperature among this package sensors. None if any sensor has that data. """
        highest = None
        for sensor in self.getSensors():
            if sensor.hasCurrent() and (highest == None or highest < sensor.getCurrent()):
                highest = sensor.getCurrent()
        return highest

    def getHighest(self):
        """ Returns highest highest temperature among this package sensors. None if any sensor has that data. """
        highest = None
        for sensor in self.getSensors():
            if sensor.hasHighest() and (highest == None or highest < sensor.getHighest()):
                highest = sensor.getHighest()
        return highest

    def getCritical(self):
        """ Returns lower critical temperature among this package sensors. None if any sensor has that data. """
        lowest = None
        for sensor in self.getSensors():
            if sensor.hasCritical() and (lowest == None or lowest > sensor.getCritical()):
                lowest = sensor.getCritical()
        return lowest

    def hasCurrent(self):
        """ True if at least a sensor of the package has the current property """
        for sensor in self.sensors:
            if sensor.hasCurrent():
                return True
        return False

    def hasHighest(self):
        """ True if at least a sensor of the package has the highest property """
        for sensor in self.sensors:
            if sensor.hasHighest():
                return True
        return False

    def hasCritical(self):
        """ True if at least a sensor of the package has the critical property """
        for sensor in self.sensors:
            if sensor.hasCritical():
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
            if sensor.hasHighest():
                attributes[f"{label} - Highest"] = sensor.getHighest()
            if sensor.hasCritical():
                attributes[ f"{label} - Critical"] = sensor.getCritical()
        return attributes


class psutilTemperatureSensor():
    def __init__(self, sensorData) -> None:
        """ sensorData is an element from the list which is the value of the the dict returned by psutil.sensors_temperatures() """
        self.label = sensorData[0]
        self.current = sensorData[1]
        self.highest = sensorData[2]
        self.critical = sensorData[3]

    def getCurrent(self):
        return self.current

    def getLabel(self) -> str:
        return self.label

    def getHighest(self):
        return self.highest

    def getCritical(self):
        return self.critical

    def hasLabel(self):
        """ True if a label is set for this sensor """
        return not self.label == None and not self.label.strip() == ""

    def hasCurrent(self):
        """ True if a current is set for this sensor """
        return not self.current == None

    def hasHighest(self):
        """ True if a highest is set for this sensor """
        return not self.highest == None

    def hasCritical(self):
        """ True if a critical is set for this sensor """
        return not self.critical == None
