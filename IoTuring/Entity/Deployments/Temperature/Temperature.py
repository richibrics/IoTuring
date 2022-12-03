import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor

KEY_SENSOR_FORMAT = "{}"

class Temperature(Entity):
    NAME = "Temperature"
    DEPENDENCIES = ["Os"]

    # I don't register packages that do not have Current temperature, so I store the registered in a list which is then checked during update
    def Initialize(self):
        self.registeredPackages = []
        sensors = psutil.sensors_temperatures()
        for device, data in sensors.items():       
            package = psutilTemperaturePackage(device, data)
            if package.hasCurrent():    
                self.registeredPackages.append(package.getLabel())
                self.RegisterEntitySensor(EntitySensor(self, self.packageNameToEntitySensorKey(package.getLabel())))
 
    def Update(self):
        sensors = psutil.sensors_temperatures()
        for device, data in sensors.items():
            package = psutilTemperaturePackage(device, data)     
            if package.getLabel() in self.registeredPackages:
                # Set main value = current of the package
                self.SetEntitySensorValue(self.packageNameToEntitySensorKey(package.getLabel()), package.getCurrent())
                # TODO set extra values
    
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
        
    # Package stats strategies here: my choose is to return always the highest among the temperatures, critical=True if a sensor has critical=True
    def getCurrent(self):
        """ Returns highest current temperature among this package sensors. None if any sensor has that data. """
        highest = None
        for sensor in self.getSensors():
            if sensor.hasCurrent() and (highest == None or highest < sensor.getCurrent()):
                highest = sensor.getCurrent()
        return highest
    
    def getHighest(self):
        """ Returns highest current temperature among this package sensors. None if any sensor has that data. """
        highest = None
        for sensor in self.getSensors():
            if sensor.hasHighest() and (highest == None or highest < sensor.getHighest()):
                highest = sensor.getHighest()
        return highest
    
    def getCritical(self):
        """ Returns True if at least a package is critical. False otherwise """
        for sensor in self.getSensors():
            if sensor.hasCritical() and sensor.getCritical():
                return True
        return False
        
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