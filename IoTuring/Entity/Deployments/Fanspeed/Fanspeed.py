import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD


VALUEFORMATTEROPTIONS_FANSPEED_RPM = ValueFormatterOptions(
    value_type=ValueFormatterOptions.TYPE_ROTATION)


FALLBACK_CONTROLLER_LABEL = "controller"
FALLBACK_FAN_LABEL = "fan"


class Fanspeed(Entity):
    """Entity to read fanspeed"""
    NAME = "Fanspeed"

    def Initialize(self) -> None:
        """Initialize the Class, setup Formatter, determin specificInitialize and specificUpdate depending on OS"""

        InitFunction = {
            OsD.LINUX: self.InitLinux
        }

        UpdateFunction = {
            OsD.LINUX: self.UpdateLinux
        }

        self.specificInitialize = InitFunction[OsD.GetOs()]
        self.specificUpdate = UpdateFunction[OsD.GetOs()]

        self.specificInitialize()

    def InitLinux(self) -> None:
        """OS dependant Init for Linux"""
        sensors = psutil.sensors_fans()
        self.Log(self.LOG_DEBUG, f"fancontrollers found:{sensors}")

        for i, controller in enumerate(sensors):
            # use FALLBACK for blank controllernames
            controllerName = controller or FALLBACK_CONTROLLER_LABEL + str(i)

            # Add extra attributes only if there are multiple fans:
            hasMultipleFans = bool(len(sensors[controller]) > 1)

            # register an entity for each controller
            self.RegisterEntitySensor(
                EntitySensor(
                    self,
                    controllerName,
                    supportsExtraAttributes=hasMultipleFans,
                    valueFormatterOptions=VALUEFORMATTEROPTIONS_FANSPEED_RPM,
                )
            )

    def Update(self) -> None:
        """placeholder for OS specificUpdate"""
        if self.specificUpdate:
            self.specificUpdate()
        else:
            raise NotImplementedError

    def UpdateLinux(self) -> None:
        """Updatemethod for Linux"""
        for controller, fans in psutil.sensors_fans().items():
            # get all fanspeed in a list and find max
            highest_fan = max([fan.current for fan in fans])
            # find higest fanspeed and assign the entity state
            self.SetEntitySensorValue(
                key=controller,
                value=highest_fan)
            # Set extra attributes {fan name : fanspeed in rpm}
            self.Log(self.LOG_DEBUG,
                     f"updating controller:{controller} with {fans}")

            # Add fans as extra attributes, if there are more than one:
            if len(fans) > 1:
                for i, fan in enumerate(fans):
                    # appy FALLBACK if label is blank
                    fanlabel = fan.label or FALLBACK_FAN_LABEL + str(i)

                    # set extra attributes for each fan
                    self.SetEntitySensorExtraAttribute(
                        controller,
                        fanlabel,
                        fan.current,
                        valueFormatterOptions=VALUEFORMATTEROPTIONS_FANSPEED_RPM,
                    )

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            # psutil docs: no attribute -> system not supported
            if not hasattr(psutil, "sensors_fans"):
                raise Exception("System not supported by psutil")
            # psutil docs: empty dict -> no fancontrollers reporting
            if not bool(psutil.sensors_fans()):
                raise Exception("No fan found in system")

        else:
            raise cls.UnsupportedOsException()
