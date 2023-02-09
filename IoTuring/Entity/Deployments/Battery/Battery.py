import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions

KEY_PERCENTAGE = 'percentage'
KEY_CHARGING_STATUS = 'charging'


class Battery(Entity):
    NAME = "Battery"

    def Initialize(self):
        self.RegisterEntitySensor(EntitySensor(self, KEY_PERCENTAGE, valueFormatterOptions=ValueFormatterOptions(ValueFormatterOptions.TYPE_PERCENTAGE)))
        
        # Check if charging state working:
        batteryInfo = self.GetBatteryInformation()
        if isinstance(batteryInfo['charging'], bool):
            self.RegisterEntitySensor(EntitySensor(self, KEY_CHARGING_STATUS))

    def PostInitialize(self):
        # Check if battery information are present
        if not psutil.sensors_battery():
            raise("No battery sensor for this host")

    def Update(self):
        batteryInfo = self.GetBatteryInformation()
        self.SetEntitySensorValue(KEY_PERCENTAGE, int(batteryInfo['level']))
        if isinstance(batteryInfo['charging'], bool):
            self.SetEntitySensorValue(
                KEY_CHARGING_STATUS, str(batteryInfo['charging']))

    def GetBatteryInformation(self):
        battery = psutil.sensors_battery()
        return {'level': battery.percent, 'charging': battery.power_plugged}
