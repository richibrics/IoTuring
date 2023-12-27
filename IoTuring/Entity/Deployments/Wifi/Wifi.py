from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Configurator.MenuPreset import MenuPreset

import psutil
import re
from socket import AddressFamily


WIFI_CHOICE_STRING = "Name: {:<15}, IP: {:<16}, MAC: {:<11}"

CONFIG_KEY_WIFI = "wifi"

KEY_SIGNAL_STRENGTH = "signal_strength"
EXTRA_KEY_ACCESS_POINT = "access_point"


class Wifi(Entity):
    NAME = "Wifi"

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
        self.getWirelessMethods = {
            OsD.WINDOWS: self.GetWirelessStrength_Windows,
            OsD.LINUX: self.GetWirelessStrength_Linux,
            OsD.MACOS: "self.GetWirelessStrength_Mac" # TODO
        }

        self.patterns = {
            'ESSID': r'ESSID:"(.*?)"',
            'Mode': r'Mode:(.*?)\s+Frequency',
            'Frequency': r'Frequency:(.*?)\s+Access Point',
            'Access Point': r'Access Point:(.*?)\s+Bit Rate',
            'Bit Rate': r'Bit Rate=(.*?)\s+Tx-Power',
            'Tx-Power': r'Tx-Power=(.*?)\s+Retry',
            'Link Quality': r'Link Quality=(.*?)\s+Signal level',
            'Signal level': r'Signal level=(.*?)\s+Rx invalid nwid',
            # Add more patterns as needed
        }

        self.platform = OsD.GetOs()
        self.specificInitialize = self.initMethods[self.platform] 
        self.specificUpdate = self.updateMethods[self.platform]
        self.specificGetWireless = self.getWirelessMethods[self.platform]

        self.configuredNic = self.GetFromConfigurations(CONFIG_KEY_WIFI)

    def InitWindows(self):
        print("InitWindows")

    def InitLinux(self):
        


    def InitMac(self):
        print("InitMac")

    def UpdateWindows(self):
        print("UpdateWindows")

    def UpdateLinux(self):
        p = self.RunCommand(["iwconfig", self.configuredNic])
        wifi_info = {}
        
        for key, pattern in self.patterns.items():
            match = re.search(pattern, p.stdout)
            if match:
                wifi_info[key] = match.group(1) # storing in the dict maybe redundant, but better readable
                
        self.SetEntitySensorValue(
            key=KEY_SIGNAL_STRENGTH,
            value=wifi_info[wifi_info[]]
        )

    def UpdateMac(self):
        print("UpdateMac")

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
    def GetWirelessStrength_Mac(self):
        raise NotImplementedError
    
    def Update(self):
        self.specificUpdate()

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
            p = cls.RunCommand(["iwconfig", nic]) # type hint return missing in subprocess.CompletedProcess
            if not bool(p.stdout): # if there is nothing in stdout for this nic it is no wireless interface
                continue
            for family in nicinfo:
                if family.family==AddressFamily.AF_INET:
                    nicip4 = family.address
                elif family.family==AddressFamily.AF_INET6:
                    nicip6 = family.address
                elif family.family==psutil.AF_LINK:
                    nicmac = family.address

            NIC_CHOICES.append(
                {
                    "name": WIFI_CHOICE_STRING.format(
                        nic, nicip4 if nicip4 else nicip6, nicmac # defaults to showing ipv4
                    ),
                    "value": nic,
                }
            )

        preset = MenuPreset()
        preset.AddEntry(
            name="Interface to check",
            key=CONFIG_KEY_WIFI,
            mandatory=True,
            question_type="select",
            choices=NIC_CHOICES,
        )
        return preset

    @classmethod
    def CheckSystemSupport(cls):  # TODO extend checks
        if OsD.IsLinux():
            if not OsD.CommandExists("iwconfig"):
                raise Exception("iwconfig not found")
        else:
            raise cls.UnsupportedOsException()