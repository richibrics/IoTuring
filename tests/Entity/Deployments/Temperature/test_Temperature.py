from IoTuring.Entity.Deployments.Temperature.Temperature import psutilTemperaturePackage, psutilTemperatureSensor

class TestPsutilTemperatureSensor:
    def testGetters(self):
        sensorData = ["sensorLabel", 91, 101, True]
        sensor = psutilTemperatureSensor(sensorData)
        assert sensor.hasLabel()
        assert sensor.hasCurrent()
        assert sensor.hasHighest()
        assert sensor.hasCritical()
        assert sensor.getLabel() == "sensorLabel"
        assert sensor.getCurrent() == 91
        assert sensor.getHighest() == 101
        assert sensor.getCritical() == True
        
        sensorData = [None, 91, 101, True]
        sensor = psutilTemperatureSensor(sensorData)
        assert not sensor.hasLabel()
        assert sensor.hasCurrent()
        assert sensor.hasHighest()
        assert sensor.hasCritical()
        
        sensorData = ["sensorLabel", None, 101, True]
        sensor = psutilTemperatureSensor(sensorData)
        assert sensor.hasLabel()
        assert not sensor.hasCurrent()
        assert sensor.hasHighest()
        assert sensor.hasCritical()
        
        sensorData = ["sensorLabel", 91, None, True]
        sensor = psutilTemperatureSensor(sensorData)
        assert sensor.hasLabel()
        assert sensor.hasCurrent()
        assert not sensor.hasHighest()
        assert sensor.hasCritical()
        
        sensorData = ["sensorLabel", 91, 101, None]
        sensor = psutilTemperatureSensor(sensorData)
        assert sensor.hasLabel()
        assert sensor.hasCurrent()
        assert sensor.hasHighest()
        assert not sensor.hasCritical()