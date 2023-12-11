import psutil

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD


VALUEFORMATTEROPTIONS_FANSPEED_RPM = ValueFormatterOptions(
            value_type=ValueFormatterOptions.TYPE_ROTATION, decimals=0)

KEY_FANSPEED = "fanspeed"
KEY_FANLABEL = "fanlabel"

FALLBACK_CONTROLLER_LABEL = "controller"
FALLBACK_FAN_LABEL = "fan"


class Fanspeed(Entity):
    """Entity to read fanspeed"""

    NAME = "Fanspeed"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self) -> None:
        """Initialize the Class, setup Formatter, determin specificInitialize and specificUpdate depending on OS"""

        self.specificInitialize = None
        self.specificUpdate = None

        if OsD.IsLinux():
            if not hasattr(psutil, "sensors_fans"): # psutil docs: no attribute -> system not supported
                raise Exception("System not supported by psutil")
            if not bool(psutil.sensors_fans()): # psutil docs: empty dict -> no fancontrollers reporting
                raise Exception("No fan found in system")
            self.specificInitialize = self.InitLinux
            self.specificUpdate = self.UpdateLinux
        
        elif OsD.IsMacos():
            raise NotImplementedError

        elif OsD.IsWindows():
            raise NotImplementedError
            
        self.specificInitialize()

    def InitLinux(self) -> None:
        """OS dependant Init for Linux"""
        self.configuredThreshold: int 
        sensors = psutil.sensors_fans()
        self.Log(self.LOG_DEBUG, f"fancontrollers found:{sensors}")
        # load all controllers from config
        self.config = self.GetConfigurations()
        for i, controllerName in enumerate(sensors):
            # use FALLBACK for blank controllernames
            if controllerName == '':
                controllerName = FALLBACK_CONTROLLER_LABEL + str(i)
            # register an entity for each controller
            self.RegisterEntitySensor(
                    EntitySensor(
                        self,
                        controllerName,
                        supportsExtraAttributes=True,
                        valueFormatterOptions=VALUEFORMATTEROPTIONS_FANSPEED_RPM, 
                    )
            )

    def Update(self) -> None:
        """placeholder for OS specificUpdate"""
        self.specificUpdate()

    def UpdateLinux(self) -> None:
        """Updatemethod for Linux"""
        for controller, fans in psutil.sensors_fans().items():
            # get all fanspeed in a list and find max
            highest_fan = max([fan.current for fan in fans])
            # find higest fanspeed and assign the entity state
            self.SetEntitySensorValue(controller, highest_fan)
            # Set extra attributes {fan name : fanspeed in rpm}
            self.Log(self.LOG_DEBUG, f"updating controller:{controller} with {fans}")
            for fan in fans:
                # appy FALLBACK if label is blank
                if fan.label == '':
                    fanlabel = FALLBACK_FAN_LABEL
                else:
                    fanlabel = fan.label
                # set extra attributes for each fan
                self.SetEntitySensorExtraAttribute(
                    controller,
                    fanlabel,
                    fan.current,
                    valueFormatterOptions=VALUEFORMATTEROPTIONS_FANSPEED_RPM,
                )