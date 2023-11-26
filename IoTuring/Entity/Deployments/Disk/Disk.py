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

    def Initialize(self) -> None:
        """Initialise the DiskUsage Entity and Register it
        """
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

    def Update(self) -> None:
        """Placeholder
        """
        pass

    def UpdateLinux(self) -> None:
        """UpdateMethod for Linux systems
        """
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentageUnix(self.configuredPath))

    def UpdateMacos(self) -> None:
        """UpdateMethod for Macos
        """
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentageUnix(self.configuredPath))

    def UpdateWindows(self) -> None:
        """UpdateMethod for Windows not implemented

        :raises NotImplementedError: windows not implemented
        """
        raise NotImplementedError
    
    def GetDiskUsedPercentageUnix(self, path: str):
        """get the current diskusage from a path, only reports for the whole disk

        :param path: path to a disk to get the usage of
        :type path: str
        :return: psutil diskusage object from disk on which path resides
        :rtype: sdiskusage
        """
        return psutil.disk_usage(path)[3]

    def parsePathfromInput(userInput) -> str:
        """User input is an Integer, parse that from list of disks

        :param userInput: userInput from ConfigurationPreset
        :type userInput: int
        :return: percentage of diskusage
        :rtype: str
        """
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
    def ConfigurationPreset(cls) -> MenuPreset:
        """Configuration for Disk Entity
        """
        preset = MenuPreset()
        preset.AddEntry(
            "enter path to check disk usage of [/]\n" + Disk.prettyPrintDisks(), CONFIG_KEY_DU_PATH, mandatory=False, modify_value_callback=Disk.parsePathfromInput
        )
        return preset
