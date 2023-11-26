import psutil
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.ValueFormat import ValueFormatter, ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

KEY_USED_PERCENTAGE = "space_used_percentage"
CONFIG_KEY_DU_PATH = "path"


class Disk(Entity):
    NAME = "Disk"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.os = OsD.GetOs()
        if self.os == OsD.OS_FIXED_VALUE_WINDOWS:
            self.Update = self.UpdateWindows
        elif self.os == OsD.OS_FIXED_VALUE_LINUX:
            self.Update = self.UpdateLinux
        elif self.os == OsD.OS_FIXED_VALUE_MACOS:
            self.Update = self.UpdateMacos

        self.config = self.GetConfigurations()
        self.configuredPath = self.config[CONFIG_KEY_DU_PATH]
        self.disks = psutil.disk_partitions()
        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_USED_PERCENTAGE,
                valueFormatterOptions=ValueFormatterOptions(
                    ValueFormatterOptions.TYPE_PERCENTAGE
                ),
            )
        )

    def Update(self):
        pass

    def UpdateLinux(self) -> None:
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentageUnix(self.configuredPath))

    def UpdateMacos(self) -> None:
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentageUnix(self.configuredPath))

    def UpdateWindows(self) -> None:
        raise NotImplementedError
    
    def GetDiskUsedPercentageUnix(self, path):    
        return psutil.disk_usage(path)[3]

    def parsePathfromInput(userInput):
        disks = psutil.disk_partitions()
        return psutil.disk_partitions()[int(userInput)][1]

    def prettyPrintDisks() -> str:
        disks = psutil.disk_partitions()
        printString = ""
        for i, disk in enumerate(disks):
            devname = disk[0]
            mountpoint = disk[1]
            printString += f"{i}: {devname}, mounted in {mountpoint}\n"
        return printString

    @classmethod
    def ConfigurationPreset(cls):
        preset = MenuPreset()
        preset.AddEntry(
            "enter path to check disk usage of [/]\n" + Disk.prettyPrintDisks(), CONFIG_KEY_DU_PATH, mandatory=False, modify_value_callback=Disk.parsePathfromInput
        )
        return preset
