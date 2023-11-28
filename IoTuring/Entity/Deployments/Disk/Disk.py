import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_USED_PERCENTAGE = "space_used_percentage"
CONFIG_KEY_DU_PATH = "path"

EXTRA_KEY_DISK_MOUNTPOINT = "Mountpoint"
EXTRA_KEY_DISK_FSTYPE = "Filesystem"
EXTRA_KEY_DISK_DEVICE = "Device"
EXTRA_KEY_DISK_TOTAL = "Total"
EXTRA_KEY_DISK_USED = "Used"
EXTRA_KEY_DISK_FREE = "Free"

VALUEFORMATOPTIONS_DISK_GB = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_BYTE, 0, "GB")


DEFAULT_PATH = {
    OsD.WINDOWS: "C:\\",
    OsD.MACOS: "/",
    OsD.LINUX: "/"
}

DISK_CHOICE_STRING = {
    OsD.WINDOWS: "Drive with Driveletter {}",
    OsD.MACOS: "{}, mounted in {}",
    OsD.LINUX: "{}, mounted in {}"
}


class Disk(Entity):
    NAME = "Disk"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self) -> None:
        """Initialise the DiskUsage Entity and Register it
        """

        self.configuredPath = self.GetFromConfigurations(CONFIG_KEY_DU_PATH)

        try:
            # Get partision info for extra attributes:
            self.disk_partition = next(
                (d for d in psutil.disk_partitions() if d.mountpoint == self.configuredPath))
        except StopIteration:
            raise Exception(f"Device not found: {self.configuredPath}")

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_USED_PERCENTAGE,
                supportsExtraAttributes=True,
                valueFormatterOptions=ValueFormatterOptions(
                    ValueFormatterOptions.TYPE_PERCENTAGE
                )
            )
        )

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_MOUNTPOINT,
            attributeValue=self.disk_partition.mountpoint)

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_FSTYPE,
            attributeValue=self.disk_partition.fstype)

        if not OsD.IsWindows():
            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_DEVICE,
                attributeValue=self.disk_partition.device)

    def Update(self) -> None:
        """UpdateMethod, psutil does not need separate behaviour on any os
        """

        usage = psutil.disk_usage(self.configuredPath)

        self.SetEntitySensorValue(
            key=KEY_USED_PERCENTAGE,
            value=usage.percent)

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_TOTAL,
            attributeValue=usage.total,
            valueFormatterOptions=VALUEFORMATOPTIONS_DISK_GB)

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_USED,
            attributeValue=usage.used,
            valueFormatterOptions=VALUEFORMATOPTIONS_DISK_GB)

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_FREE,
            attributeValue=usage.free,
            valueFormatterOptions=VALUEFORMATOPTIONS_DISK_GB)

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:

        # Get the choices for menu:
        DISK_CHOICES = []

        for disk in psutil.disk_partitions():
            DISK_CHOICES.append(
                {"name":
                 DISK_CHOICE_STRING[OsD.GetOs()].format(
                     disk.device, disk.mountpoint),
                 "value": disk.mountpoint}
            )

        preset = MenuPreset()
        preset.AddEntry(name="Drive to check",
                        key=CONFIG_KEY_DU_PATH, mandatory=False,
                        question_type="select", choices=DISK_CHOICES)
        return preset
