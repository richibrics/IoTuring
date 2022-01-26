import psutil
from Entity.Entity import Entity 


TOPIC_PERCENTAGE = 'battery/battery_level_percentage'
TOPIC_CHARGING_STATUS = 'battery/battery_charging'


class Battery(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC_PERCENTAGE)
        self.AddTopic(TOPIC_CHARGING_STATUS)

    def PostInitialize(self):
        # Check if battery infomration are present
        if not psutil.sensors_battery():
            raise("No battery sensor for this host")

    def Update(self):
        batteryInfo = self.GetBatteryInformation()
        self.SetTopicValue(TOPIC_PERCENTAGE, int(batteryInfo['level']),self.ValueFormatter.TYPE_PERCENTAGE)
        self.SetTopicValue(TOPIC_CHARGING_STATUS, str(batteryInfo['charging']))

    def GetBatteryInformation(self):
        battery = psutil.sensors_battery()
        return {'level': battery.percent, 'charging': battery.power_plugged}
