import platform
from Entity.Entity import Entity
from Entity.EntityData import EntitySensor
from Entity import consts
import json

psvutil_response = '{"acpitz": [{"label": "", "current": 45}], "coretemp": [{"label": "Package id 0", "current": 45}, {"label": "Core 0", "current": 45}]}'

KEY_SENSOR_FORMAT = "sensor_{}"

class Temperature(Entity):
    NAME = "Temperature"

    def Initialize(self):
        sensors = psvutil.sensors_temperatures()
        for device, data in sensors.items():
            print(KEY_SENSOR_FORMAT.format(device))
            self.RegisterEntitySensor(EntitySensor(self,KEY_SENSOR_FORMAT.format(device)))
 
    def Update(self):
        pass

class psvutil:
    def sensors_temperatures():
        return json.loads(psvutil_response)
