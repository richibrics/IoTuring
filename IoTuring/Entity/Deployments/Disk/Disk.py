import psutil
from time import time

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_USED_PERCENTAGE = "space_used_percentage"
CONFIG_KEY_DU_PATH = "path"

CONFIG_KEY_DISKIO = "IO"

EXTRA_KEY_DISK_MOUNTPOINT = "Mountpoint"
EXTRA_KEY_DISK_FSTYPE = "Filesystem"
EXTRA_KEY_DISK_DEVICE = "Device"
EXTRA_KEY_DISK_TOTAL = "Total"
EXTRA_KEY_DISK_USED = "Used"
EXTRA_KEY_DISK_FREE = "Free"
EXTRA_KEY_DISK_READ_COUNT = "Read count"
EXTRA_KEY_DISK_WRITE_COUNT = "Write count"
EXTRA_KEY_DISK_READ_BYTES = "Read bytes"
EXTRA_KEY_DISK_WRITE_BYTES = "Write bytes"
EXTRA_KEY_DISK_READ_TIME = "Read time"
EXTRA_KEY_DISK_WRTIE_TIME = "Write time"
EXTRA_KEY_DISK_READ_RATE = "Read rate"
EXTRA_KEY_DISK_WRITE_RATE = "Write rate"
EXTRA_KEY_DISK_READ_MERGED_COUNT = "Read merged count"
EXTRA_KEY_DISK_WRITE_MERGED_COUNT = "Write merged count"
EXTRA_KEY_DISK_BUSY_TIME = "Busy time"


VALUEFORMATOPTIONS_GB = ValueFormatterOptions(ValueFormatterOptions.TYPE_BYTE, 0, "GB")

VALUEFORMATOPTIONS_B = ValueFormatterOptions(ValueFormatterOptions.TYPE_BYTE, 0, "B")

VALUEFORMATOPTIONS_TIME = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_TIME, 0, "ms"
)

VALUEFORMATOPTIONS_PERCENT = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_PERCENTAGE, 1, "%"
)

VALUEFORMATOPTIONS_BpS = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_BYTE_PER_SECOND, 0, "B/s"
)

DEFAULT_PATH = {OsD.WINDOWS: "C:\\", OsD.MACOS: "/", OsD.LINUX: "/"}

DISK_CHOICE_STRING = {
    OsD.WINDOWS: "Drive with Driveletter {}",
    OsD.MACOS: "{}, mounted in {}",
    OsD.LINUX: "{}, mounted in {}",
}


class Disk(Entity):
    NAME = "Disk"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self) -> None:
        """Initialise the DiskUsage Entity and Register it"""

        self.configuredPath = self.GetFromConfigurations(CONFIG_KEY_DU_PATH)
        self.configuredIo = self.GetFromConfigurations(CONFIG_KEY_DISKIO)
        self.lastUpdate = ""

        try:
            # Get partition info for extra attributes:
            self.disk_partition = next(
                (
                    d
                    for d in psutil.disk_partitions()
                    if d.mountpoint == self.configuredPath
                )
            )
        except StopIteration:
            raise Exception(f"Device not found: {self.configuredPath}")

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_USED_PERCENTAGE,
                supportsExtraAttributes=True,
                valueFormatterOptions=ValueFormatterOptions(
                    ValueFormatterOptions.TYPE_PERCENTAGE
                ),
            )
        )

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_MOUNTPOINT,
            attributeValue=self.disk_partition.mountpoint,
        )

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_FSTYPE,
            attributeValue=self.disk_partition.fstype,
        )

        if not OsD.IsWindows():
            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_DEVICE,
                attributeValue=self.disk_partition.device,
            )

    def Update(self) -> None:
        """UpdateMethod, psutil does not need separate behaviour on any os"""

        usage = psutil.disk_usage(self.configuredPath)

        self.SetEntitySensorValue(key=KEY_USED_PERCENTAGE, value=usage.percent)

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_TOTAL,
            attributeValue=usage.total,
            valueFormatterOptions=VALUEFORMATOPTIONS_GB,
        )

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_USED,
            attributeValue=usage.used,
            valueFormatterOptions=VALUEFORMATOPTIONS_GB,
        )

        self.SetEntitySensorExtraAttribute(
            sensorDataKey=KEY_USED_PERCENTAGE,
            attributeKey=EXTRA_KEY_DISK_FREE,
            attributeValue=usage.free,
            valueFormatterOptions=VALUEFORMATOPTIONS_GB,
        )

        if self.configuredIo and OsD.IsLinux():
            # the following are supported on nearly every OS, Windows drivenames/devnames are complicated, so no Windows support

            devname = self.disk_partition.device.split("/")[-1]
            disk_io: psutil._common.sdiskio = psutil.disk_io_counters(perdisk=True)[
                devname
            ]
            currentTime = time()
            if self.lastUpdate:
                timeSinceLastUpdate = currentTime - self.lastUpdate
                readrate = (
                    disk_io.read_bytes - self.lastReadBytes
                ) / timeSinceLastUpdate
                writerate = (
                    disk_io.write_bytes - self.lastWriteBytes
                ) / timeSinceLastUpdate
            else:
                readrate = 0
                writerate = 0

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_READ_COUNT,
                attributeValue=disk_io.read_count,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_WRITE_COUNT,
                attributeValue=disk_io.write_count,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_READ_BYTES,
                attributeValue=disk_io.read_bytes,
                valueFormatterOptions=VALUEFORMATOPTIONS_B,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_WRITE_BYTES,
                attributeValue=disk_io.write_bytes,
                valueFormatterOptions=VALUEFORMATOPTIONS_B,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_READ_TIME,
                attributeValue=disk_io.read_time,
                valueFormatterOptions=VALUEFORMATOPTIONS_TIME,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_WRTIE_TIME,
                attributeValue=disk_io.write_time,
                valueFormatterOptions=VALUEFORMATOPTIONS_TIME,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_READ_RATE,
                attributeValue=readrate,
                valueFormatterOptions=VALUEFORMATOPTIONS_BpS,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_WRITE_RATE,
                attributeValue=writerate,
                valueFormatterOptions=VALUEFORMATOPTIONS_BpS,
            )

            # the following are only supported in linux
            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_READ_MERGED_COUNT,
                attributeValue=disk_io.read_merged_count,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_WRITE_MERGED_COUNT,
                attributeValue=disk_io.write_merged_count,
            )

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=KEY_USED_PERCENTAGE,
                attributeKey=EXTRA_KEY_DISK_BUSY_TIME,
                attributeValue=disk_io.busy_time,
                valueFormatterOptions=VALUEFORMATOPTIONS_TIME,
            )

            self.lastUpdate = time()
            self.lastReadBytes = disk_io.read_bytes
            self.lastWriteBytes = disk_io.write_bytes

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        # Get the choices for menu:
        DISK_CHOICES = []

        for disk in psutil.disk_partitions():
            DISK_CHOICES.append(
                {
                    "name": DISK_CHOICE_STRING[OsD.GetOs()].format(
                        disk.device, disk.mountpoint
                    ),
                    "value": disk.mountpoint,
                }
            )

        preset = MenuPreset()
        preset.AddEntry(
            name="Drive to check",
            key=CONFIG_KEY_DU_PATH,
            mandatory=True,
            question_type="select",
            choices=DISK_CHOICES,
        )
        if OsD.IsLinux():
            preset.AddEntry(
                name="Update DiskIO",
                key=CONFIG_KEY_DISKIO,
                mandatory=True,
                question_type="yesno",
            )
        return preset
