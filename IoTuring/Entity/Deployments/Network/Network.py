# Wireless strength method taken from: https://github.com/s7jones/Wifi-Signal-Plotter/
import re
import subprocess

from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Configurator.MenuPreset import MenuPreset

import psutil
from socket import AddressFamily

VALUEFORMATTEROPTIONS_BYTE = ValueFormatterOptions(
    value_type=ValueFormatterOptions.TYPE_BYTE
)
VALUEFORMATTEROPTIONS_RADIOPOWER = ValueFormatterOptions(
    value_type=ValueFormatterOptions.TYPE_RADIOPOWER
)

NIC_CHOICE_STRING = "Name: {:<15}, IP: {:<16}, MAC: {:<11}"

KEY_SIGNAL_STRENGTH = "signal_strength"
CONFIG_KEY_NIC = "nicname"
CONFIG_KEY_WIRELESS = "wireless"
NOT_WIRELESS_STRING = "no wireless extensions."

# old stuff
DOWNLOAD_TRAFFIC_TOPIC = "network/traffic/bytes_recv"
UPLOAD_TRAFFIC_TOPIC = "network/traffic/bytes_sent"

NIC_ADDRESS_TOPIC = "network/interfaces/{}/private_address"  # nic name in brackets
NIC_SIGNAL_STRENGTH_TOPIC = "network/interfaces/{}/signal_strength"  # nic name in brackets - 0 for non wireless nic


SIZE_OPTION_KEY = "size"
EXCLUDE_INTERFACES_CONTENT_OPTION_KEY = "exclude_interfaces"
RENAME_INTERFACES_CONTENT_OPTION_KEY = "rename_interfaces"

NIC_PRIVATE_ADDRESS_DISCOVERY_NAME_FORMAT = "{} private ip"
NIC_PRIVATE_ADDRESS_DISCOVERY_ICON = "mdi:ip-network"

NIC_SIGNAL_STRENGTH_DISCOVERY_NAME_FORMAT = "{} signal strength"
NIC_SIGNAL_STRENGTH_DISCOVERY_ICON = "mdi:network-strength-3"

# Windows returns strength in %, linux in dB
NIC_SIGNAL_STRENGTH_DISCOVERY_UNIT_OF_MEASUREMENT_LINUX = "dB"
NIC_SIGNAL_STRENGTH_DISCOVERY_UNIT_OF_MEASUREMENT_WINDOWS = "%"


class Network(Entity):
    NAME = "Network"

    def Initialize(self):
        self.initMethods = {
            OsD.WINDOWS: self.InitWindows,
            OsD.LINUX: self.InitLinux,
            OsD.MACOS: self.InitMac,
        }
        self.updateMethods = {
            OsD.WINDOWS: self.UpdateWindows,
            OsD.LINUX: self.UpdateLinux,
            OsD.MACOS: self.UpdateMac,
        }
        self.platform = OsD.GetOs()
        self.specificInitialize = self.initMethods[self.platform]
        self.specificUpdate = self.updateMethods[self.platform]

        self.configuredNic = self.GetFromConfigurations(CONFIG_KEY_NIC)

        if self.GetFromConfigurations(CONFIG_KEY_WIRELESS) == 'Y':
            self.isWireless = True
            self.RegisterEntitySensor(
                EntitySensor(
                    self,
                    KEY_SIGNAL_STRENGTH,
                    supportsExtraAttributes=True,
                    valueFormatterOptions=VALUEFORMATTEROPTIONS_RADIOPOWER,
                )
            )
        else:
            self.isWireless = False # There has to be a smoother way, works though
            self. RegisterEntitySensor(
                EntitySensor(
                    self,
                    
                )
            )

        
      

        # # Get list of interfaces to ignore: if not specified: [], if set only a string: [string], if set a list: [item1,item2] -> I always have a list (else schema not validated)
        # self.excludeInterfaces=self.Configurator.ReturnAsList(self.GetOption([self.consts.CONTENTS_OPTION_KEY,EXCLUDE_INTERFACES_CONTENT_OPTION_KEY],[]))
        # self.excludeInterfaces = self.GetFromConfigurations(key=EXCLUDE_INTERFACES_CONTENT_OPTION_KEY)

        # # Interfaces
        # self.nicsToRegister = []
        # for nic in netifaces.interfaces():
        #     # If I don't exclude it and if has a private address (AF_INET=2)
        #     if '{' not in self.GetNicName(nic) and self.GetNicName(nic) not in self.excludeInterfaces and netifaces.AF_INET in netifaces.ifaddresses(nic):
        #         self.AddTopic(self.InterfaceTopicFormat(NIC_ADDRESS_TOPIC,self.GetNicName(nic)))
        #         self.AddTopic(self.InterfaceTopicFormat(NIC_SIGNAL_STRENGTH_TOPIC,self.GetNicName(nic)))
        #         self.nics.append(nic)
        #         self.Log(self.Logger.LOG_DEBUG, "Added " + self.GetNicName(nic,getRenamed=False)+ " interface")
        #         if self.GetNicName(nic) != self.GetNicName(nic, getRenamed= False):
        #             self.Log(self.Logger.LOG_DEBUG, "Renamed " + self.GetNicName(nic,getRenamed=False)+ " to " + self.GetNicName(nic))
        #         self.RegisterEntitySensor()

        # Traffic data
        # self.AddTopic(DOWNLOAD_TRAFFIC_TOPIC)
        # self.AddTopic(UPLOAD_TRAFFIC_TOPIC)
        self.specificInitialize()

    def InitWindows(self):
        raise NotImplementedError

    def InitLinux(self):
        print("init")  # TODO

    def InitMac(self):
        raise NotImplementedError

    def UpdateWindows(self):
        self.GetEntitySensorValue(self.GetWirelessStrength_Windows())

    def UpdateLinux(self):

        if self.isWireless:
            self.SetEntitySensorValue(
                key=KEY_SIGNAL_STRENGTH, 
                value=self.GetWirelessStrength_Linux()
            )
        else:
            self.SetEntitySensorValue(

            )

    def UpdateMac(self):
        raise NotImplementedError

    # def PostInitialize(self):
    #     global supports_linux_signal_strength,supports_win_signal_strength,supports_macos_signal_strength

    #     os = self.GetOS()

    #     self.UpdateWirelessSignalStrenghtSpecificFunction = None   # Specific function for this os/de, set this here to avoid all if else except at each update

    #     if(os == self.consts.FIXED_VALUE_OS_WINDOWS):
    #         self.NIC_SIGNAL_STRENGTH_DISCOVERY_UNIT_OF_MEASUREMENT= NIC_SIGNAL_STRENGTH_DISCOVERY_UNIT_OF_MEASUREMENT_WINDOWS
    #         self.UpdateWirelessSignalStrenghtSpecificFunction = self.GetWirelessStrenght_Windows

    #         if not supports_win_signal_strength:
    #             self.Log(self.Logger.LOG_ERROR,"Error with signal strength sensor, have you installed all the dependencies ? (winreg, netifaces)")
    #             # If not supported, I remove the signal strength topic (also discovery won't include anymore this topic)
    #             self.RemoveSignalStrenghtTopics()
    #             self.supports_signal_strength = False

    #     elif(os ==  self.consts.FIXED_VALUE_OS_LINUX):
    #         self.NIC_SIGNAL_STRENGTH_DISCOVERY_UNIT_OF_MEASUREMENT= NIC_SIGNAL_STRENGTH_DISCOVERY_UNIT_OF_MEASUREMENT_LINUX
    #         self.UpdateWirelessSignalStrenghtSpecificFunction = self.GetWirelessStrenght_Linux

    #         if not supports_linux_signal_strength:
    #             self.Log(self.Logger.LOG_ERROR,"Error with signal strength sensor, have you installed all the dependencies ? (netifaces)")
    #             # If not supported, I remove the signal strength topic (also discovery won't include anymore this topic)
    #             self.RemoveSignalStrenghtTopics()
    #             self.supports_signal_strength = False

    #     # elif(Get_Operating_System() ==  self.consts.FIXED_VALUE_OS_MACOS):
    #     #    self.UpdateSpecificFunction =  NOT SUPPORTED

    #     else:
    #         self.Log(self.Logger.LOG_ERROR, 'No wireless signal strength sensor available for this operating system')
    #         # If not supported, I remove the signal strength topic (also discovery won't include anymore this topic)
    #         self.RemoveSignalStrenghtTopics()
    #         self.supports_signal_strength = False

    def Update(self):
        self.specificUpdate()
        
    # Signal strength methods:
    def GetWirelessStrength_Linux(self):
        p = self.RunCommand(["iwconfig", self.configuredNic])
        if p.stderr:
            raise Exception("error during iwconfig")
        elif p.stdout:
            signalStrength = re.findall(f"Signal level=(-[0-9]+) dBm", p.stdout)
        return signalStrength[0]

    def GetWirelessStrength_Windows(self):
        p = subprocess.Popen(
            "netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out = p.stdout.read().decode(errors="ignore")
        if "Segnale" in out:  # Italian support
            m = re.findall(
                "Nome.*?:.*? ([A-z0-9 \-]*).*?Segnale.*?:.*?([0-9]*)%", out, re.DOTALL
            )
        elif "Signal" in out:  # English support
            m = re.findall(
                "Nome.*?:.*?([A-z0-9 ]*).*?Signal.*?:.*?([0-9]*)%", out, re.DOTALL
            )
        else:
            self.Log(
                self.Logger.LOG_ERROR,
                "Can't get signal strength data in your region. Please open a Git issue with and show the output of this command in the CMD: 'netsh wlan show interfaces' ",
            )
            self.supports_signal_strength = False
            # TODO Remove the signal strength topic for all the inets here !
        p.communicate()
        return m

    def GetNicName(self, nic, getRenamed=True):
        # On windows, the network interface name has only the id "{......}"
        name = nic
        try:
            if "{" in nic:
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                reg_key = winreg.OpenKey(
                    reg,
                    r"SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}",
                )
                reg_subkey = winreg.OpenKey(reg_key, nic + r"\Connection")
                name = winreg.QueryValueEx(reg_subkey, "Name")[0]
        except:
            name = nic

        if getRenamed:
            # In configuration, user can set a rename interfaces dict, with key=original name, value=new name
            rename_dict = self.GetOption(
                [self.consts.CONTENTS_OPTION_KEY, RENAME_INTERFACES_CONTENT_OPTION_KEY],
                {},
            )
            if name in rename_dict:
                return rename_dict[name]

        return name

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        # Get the choices for menu:
        NIC_CHOICES = []

        nics = psutil.net_if_addrs()

        for nic in nics:
            nicinfo = nics[nic]
            # try to get nic ip
            nicip4 = ""
            nicip6 = ""
            nicmac = ""

            for family in nicinfo:
                if family.family==AddressFamily.AF_INET:
                    nicip4 = family.address
                elif family.family==AddressFamily.AF_INET6:
                    nicip6 = family.address
                elif family.family==psutil.AF_LINK:
                    nicmac = family.address

            NIC_CHOICES.append(
                {
                    "name": NIC_CHOICE_STRING.format(
                        nic, nicip4 if nicip4 else nicip6, nicmac # defaults to shwoing ipv4
                    ),
                     
                    "value": nic,
                }
            )

        preset = MenuPreset()
        preset.AddEntry(
            name="Interface to check",
            key=CONFIG_KEY_NIC,
            mandatory=True,
            question_type="select",
            choices=NIC_CHOICES,
        )
        preset.AddEntry(
            name="Is it a wireless interface?",
            key=CONFIG_KEY_WIRELESS,
            mandatory=False,
            question_type="yesno",
            default='N'
        )
        return preset


    @classmethod
    def CheckSystemSupport(cls): # TODO extend checks
        if OsD.IsLinux():
            if not OsD.CommandExists("iwconfig"):
                raise Exception("iwconfig not found")
        else:
            raise cls.UnsupportedOsException()

# Example in configuration:
#
#      - Network:
#          value_format: # for traffic information
#            size: MB // SIZE_....BYTE constant
#          content:
#             exclude_interfaces:
#               - lo
#               - VirtualBox Host-Only Network
#             rename_interfaces:
#               wlp0s20f3: Wi-Fi
