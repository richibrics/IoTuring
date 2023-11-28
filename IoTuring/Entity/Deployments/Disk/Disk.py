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
    CONFIG_QUESTION = "which Drive shall be checked"
    DEFAULT_PATH_UNIX = "/"
    DEFAULT_PATH_WINDOWS = "C:\\"

    def Initialize(self) -> None:
        """Initialise the DiskUsage Entity and Register it
        """

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
        """UpdateMethod, psutil does not need separate behaviour on any os
        """
        self.SetEntitySensorValue(KEY_USED_PERCENTAGE, self.GetDiskUsedPercentage(self.configuredPath))
    
    def GetDiskUsedPercentage(self, path: str):
        """get the current diskusage from a path, only reports for the whole disk

        :param path: path to a disk to get the usage of
        :type path: str
        :return: psutil diskusage object from disk on which path resides
        :rtype: sdiskusage
        """
        return psutil.disk_usage(path)[3]

    @staticmethod
    def parsePathfromInput(userInput) -> str:
        """User input is an Integer, parse that from list of disks

        :param userInput: userInput from ConfigurationPreset
        :type userInput: int
        :return: percentage of diskusage
        :rtype: str
        """
        return psutil.disk_partitions()[int(userInput)][1]

    @staticmethod
    def prettyPrintDisksUnix() -> str:
        disks = psutil.disk_partitions()
        printString = ""
        for i, disk in enumerate(disks):
            printString += f"\n{i}: {disk.device}, mounted in {disk.mountpoint}"
        return printString
    
    @staticmethod
    def prettyPrintDisksWindows() -> str:
        disks = psutil.disk_partitions()
        printString = ""
        for i, disk in enumerate(disks):
            printString += f"\n{i}: Drive with Driveletter {disk.device}"
        return printString

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:

        OS = OsD.GetOs()
        if OS == OsD.OS_FIXED_VALUE_WINDOWS:
            DEFAULT_PATH = Disk.DEFAULT_PATH_WINDOWS
            prettyPrintDisks = Disk.prettyPrintDisksWindows
        
        elif OS == OsD.OS_FIXED_VALUE_LINUX:
            DEFAULT_PATH = Disk.DEFAULT_PATH_UNIX
            prettyPrintDisks = Disk.prettyPrintDisksUnix

        elif OS == OsD.OS_FIXED_VALUE_MACOS:
            DEFAULT_PATH = Disk.DEFAULT_PATH_UNIX
            prettyPrintDisks = Disk.prettyPrintDisksUnix

        preset = MenuPreset()
        preset.AddEntry(
            Disk.CONFIG_QUESTION + prettyPrintDisks(), CONFIG_KEY_DU_PATH, mandatory=False, modify_value_callback=Disk.parsePathfromInput, default=DEFAULT_PATH
        )
        return preset
