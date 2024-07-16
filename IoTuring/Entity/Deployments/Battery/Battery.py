from __future__ import annotations
from typing import TypedDict, Dict
import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions

KEY_PERCENTAGE = 'percentage'
KEY_CHARGING_STATUS = 'charging'

class BatteryInformation(TypedDict):
        level: int
        charging: bool

class Battery(Entity):
    NAME = "Battery"
    supports_charge = False

    def Initialize(self):

        # This should raise error if no battery:
        batteryInfo = self.GetBatteryInformation()

        self.RegisterEntitySensor(EntitySensor(
            self, KEY_PERCENTAGE, valueFormatterOptions=ValueFormatterOptions(ValueFormatterOptions.TYPE_PERCENTAGE)))

        # Check if charging state working:
        if isinstance(batteryInfo['charging'], bool):
            self.supports_charge = True
            self.RegisterEntitySensor(EntitySensor(self, KEY_CHARGING_STATUS))

    def Update(self):
        batteryInfo = self.GetBatteryInformation()

        self.SetEntitySensorValue(
            KEY_PERCENTAGE, int(batteryInfo['level']))

        if self.supports_charge:
            self.SetEntitySensorValue(
                KEY_CHARGING_STATUS, str(batteryInfo['charging']))

    def GetBatteryInformation(self) -> BatteryInformation:
        battery = psutil.sensors_battery()
        if not battery:
            raise Exception("No battery sensor for this host")

        return BatteryInformation({'level': battery.percent, 'charging': battery.power_plugged})
