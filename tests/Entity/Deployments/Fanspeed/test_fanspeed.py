from IoTuring.Entity.ToImplement.FanSpeed.FanSpeeds import psutilFanspeedPackage, psutilFanspeedSensor

class TestPsutilFanspeedSensor:
    def testGetters(self):
        sensorData = ["sensorLabel", 1250]
        sensor = psutilFanspeedSensor(sensorData)
        assert sensor.hasLabel()
        assert sensor.hasCurrent()
        assert sensor.getLabel() == "sensorLabel"
        assert sensor.getCurrent() == 91
        
        sensorData = [None, 0]
        sensor = psutilFanspeedSensor(sensorData)
        assert not sensor.hasLabel()
        assert sensor.hasCurrent()
        
        sensorData = ["sensorLabel", None]
        sensor = psutilFanspeedSensor(sensorData)
        assert sensor.hasLabel()
        assert not sensor.hasCurrent()
        

class TestPsutilFanspeedPackage:# TODO
    def testHas(self):
        # package p has attribute (result = True) iff at least a sensor of p has that attribute
        packageData = []
        packageData.append(["sensorLabel", 1250])
        packageData.append(["sensorLabel", 900])
        package = psutilFanspeedPackage("pkg", packageData)
        assert package.hasCurrent()
        
        packageData = []
        packageData.append(["sensorLabel", None])
        packageData.append(["sensorLabel", 90, 99, False])
        package = psutilTemperaturePackage("pkg", packageData)
        assert package.hasCurrent()
        assert package.hasHighest()
        assert package.hasCritical()
        
        packageData = []
        packageData.append(["sensorLabel", 11, 99, True])
        packageData.append(["sensorLabel", None, None, None])
        package = psutilTemperaturePackage("pkg", packageData)
        assert package.hasCurrent()
        assert package.hasHighest()
        assert package.hasCritical()
        
        packageData = []
        packageData.append(["sensorLabel", 11, None, True])
        packageData.append(["sensorLabel", None, 156, None])
        package = psutilTemperaturePackage("pkg", packageData)
        assert package.hasCurrent()
        assert package.hasHighest()
        assert package.hasCritical()
        
        packageData = []
        packageData.append(["sensorLabel", None, None, None])
        packageData.append(["sensorLabel", None, None, None])
        package = psutilTemperaturePackage("pkg", packageData)
        assert not package.hasCurrent()
        assert not package.hasHighest()
        assert not package.hasCritical()
        
        packageData = []
        packageData.append(["sensorLabel", 12, None, None])
        packageData.append(["sensorLabel", None, None, None])
        package = psutilTemperaturePackage("pkg", packageData)
        assert package.hasCurrent()
        assert not package.hasHighest()
        assert not package.hasCritical()
        
        packageData = []
        packageData.append(["sensorLabel", None, None, None])
        packageData.append(["sensorLabel", None, 35, None])
        package = psutilTemperaturePackage("pkg", packageData)
        assert not package.hasCurrent()
        assert package.hasHighest()
        assert not package.hasCritical()
        
        packageData = []
        packageData.append(["sensorLabel", None, None, False])
        packageData.append(["sensorLabel", None, None, None])
        package = psutilTemperaturePackage("pkg", packageData)
        assert not package.hasCurrent()
        assert not package.hasHighest()
        assert package.hasCritical()
        
        
    def testGetters(self): # TODO
        packageName = "pkg"
        
        packageData = []
        packageData.append(["sensorLabel1", 80, 101, 11])
        packageData.append(["sensorLabel2", 90, 99, 12])
        package = psutilTemperaturePackage(packageName, packageData)
        assert package.getSensors()[0].getLabel() == "sensorLabel1"
        assert package.getSensors()[0].getCurrent() == 80
        assert package.getSensors()[0].getHighest() == 101
        assert package.getSensors()[0].getCritical() == 11
        assert package.getSensors()[1].getLabel() == "sensorLabel2"
        assert package.getSensors()[1].getCurrent() == 90
        assert package.getSensors()[1].getHighest() == 99
        assert package.getSensors()[1].getCritical() == 12
        assert package.getLabel() == packageName
        assert package.getCurrent() == 90 # highest of the two sensors
        assert package.getHighest() == 101 # highest of the two sensors
        assert package.getCritical() == 11 # lowest of the two sensors
        
        packageData = []
        packageData.append(["sensorLabel", 29, 101, 22])
        packageData.append(["sensorLabel", 10, 102, 10])
        package = psutilTemperaturePackage(packageName, packageData)
        assert package.getCurrent() == 29 # highest of the two sensors
        assert package.getHighest() == 102 # highest of the two sensors
        assert package.getCritical() == 10 # lowest of the two sensors
        
        packageData = []
        packageData.append(["sensorLabel", None, 101, None])
        packageData.append(["sensorLabel", 10, None, 33])
        package = psutilTemperaturePackage(packageName, packageData)
        assert package.getCurrent() == 10 # highest of the two sensors
        assert package.getHighest() == 101 # highest of the two sensors
        assert package.getCritical() == 33 # lowest of the two sensors