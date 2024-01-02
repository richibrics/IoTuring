from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Configurator.MenuPreset import MenuPreset

import subprocess
import psutil
import re
from socket import AddressFamily


WIFI_CHOICE_STRING = "Name: {:<15}, IP: {:<16}, MAC: {:<11}"

CONFIG_KEY_WIFI = "wifi"

KEY_SIGNAL_STRENGTH = "signal_strength"

# WINDOWS
EXTRA_KEY_SSID = "ssid"
EXTRA_KEY_BSSID = "bssid"
EXTRA_KEY_SIGNAL = "signal"
EXTRA_KEY_CHANNEL = "channel"
EXTRA_KEY_AUTHENTICATION = "authentication"
EXTRA_KEY_ENCRYPTION = "encryption"
EXTRA_KEY_RADIO_TYPE = "radio_type"
# LINUX
EXTRA_KEY_ESSID = "essid"
EXTRA_KEY_MODE = "mode"
EXTRA_KEY_FREQUENCY = "frequency"
EXTRA_KEY_ACCESS_POINT = "access_point"
EXTRA_KEY_BIT_RATE = "bit_rate"
EXTRA_KEY_TX_POWER = "tx_power"
EXTRA_KEY_LINK_QUALITY = "link_quality"
EXTRA_KEY_SIGNAL_LEVEL = "signal_level"
# MACOS
EXTRA_KEY_SSID = "ssid"
# EXTRA_KEY_BSSID = "bssid" # already in windows
EXTRA_KEY_RSSI = "rssi"
# EXTRA_KEY_CHANNEL = "channel" # already in windows
EXTRA_KEY_HT = "ht"
EXTRA_KEY_SECURITY = "security"
EXTRA_KEY_LINK_AUTH = "link_auth"
EXTRA_KEY_LINK_ENC = "link_enc"

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
            OsD.MACOS: "self.GetWirelessStrength_Mac",
        }

        self.patterns = {
            OsD.WINDOWS : {
                'SSID': r'\bSSID\s+: (.*)',
                'BSSID': r'\bBSSID\s+: (.*)',
                'Signal': r'\bSignal\s+: (.*)%',
                'Channel': r'\bChannel\s+: (\d+)',
                'Authentication': r'\bAuthentication\s+: (.*)',
                'Encryption': r'\bEncryption\s+: (.*)',
                'Radio Type': r'\bRadio Type\s+: (.*)'
            },
            OsD.LINUX : {
                'ESSID': r'ESSID:"(.*?)"',
                'Mode': r'Mode:(.*?)\s+Frequency',
                'Frequency': r'Frequency:(.*?)\s+Access Point',
                'Access Point': r'Access Point:(.*?)\s+Bit Rate',
                'Bit Rate': r'Bit Rate=(.*?)\s+Tx-Power',
                'Tx Power': r'Tx-Power=(.*?)\s+Retry',
                'Link Quality': r'Link Quality=(.*?)\s+Signal level',
                'Signal level': r'Signal level=(.*?)\s+Rx invalid nwid',
            },
            OsD.MACOS : {
                'SSID': r'\bSSID: (.*)',
                'BSSID': r'\bBSSID: (.*)',
                'RSSI': r'\bagrCtlRSSI: (-\d+)',
                'Channel': r'\bchannel: (\d+)',
                'HT': r'\bHT (.*): (\w+)',
                'Security': r'\bsecurity: (.*)',
                'Link Auth': r'\blink auth: (.*)',
                'Link Enc': r'\blink auth: (.*)'
            }
        }

        self.platform = OsD.GetOs()
        self.specificInitialize = self.initMethods[self.platform]
        self.specificUpdate = self.updateMethods[self.platform]
        self.specificGetWireless = self.getWirelessMethods[self.platform]

        self.configuredNic = self.GetFromConfigurations(CONFIG_KEY_WIFI)

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_SIGNAL_STRENGTH,
                supportsExtraAttributes=True,
                valueFormatterOptions=ValueFormatterOptions(
                    ValueFormatterOptions.TYPE_RADIOPOWER
                )
            )
        )

    def InitWindows(self):
        print("InitWindows")

    def InitLinux(self):
        print("InitLinux")

    def InitMac(self):
        print("InitMac")

    def UpdateWindows(self):
        p = self.RunCommand(["netsh", "wlan", "show", "interfaces"])
        if p.stdout:
            self.wifiInfo = self.GetWirelessInfo(p.stdout)

    def UpdateLinux(self):
        p = self.RunCommand(["iwconfig", self.configuredNic])
        if p.stdout:
            self.wifiInfo = self.GetWirelessInfo(p.stdout)

    def UpdateMac(self): # TODO check if any of this even works GPT was cooking
        p = self.RunCommand(["airport", "-I"])
        if p.stdout:
            self.wifiInfo = self.GetWirelessInfo(p.stdout)

    def GetWirelessInfo(self, stdout):
        wifi_info = {}
        for key, pattern in self.patterns[self.platform].items():
            match = re.search(pattern, stdout, re.IGNORECASE)
            if match:
                wifi_info[key] = match.group(1) if match.group(1) else match.group(0)
                if key == "RSSI" or "Signal" or "Signal level":
                    self.SetEntitySensorValue(
                        key=KEY_SIGNAL_STRENGTH,
                        value=wifi_info[key]
                    )
                else:
                    extraKey = "EXTRA_KEY_" + key.upper().replace(" ", "_")
                    self.SetEntitySensorExtraAttribute(
                        sensorDataKey=KEY_SIGNAL_STRENGTH,
                        attributeKey=globals()[extraKey],
                        attributeValue=wifi_info[key]
                    )

        return wifi_info

    def GetWirelessStrength_Linux(self):
        p = self.RunCommand(["iwconfig", self.configuredNic])
        if p.stderr:
            raise Exception("error during iwconfig")
        elif p.stdout:
            signalStrength = re.findall(f"Signal level=(-[0-9]+) dBm", p.stdout)
        return signalStrength[0]

    def GetWirelessStrength_Windows(self):
        p = self.RunCommand(
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
                self.LOG_ERROR,
                "Can't get signal strength data in your region. Please open a Git issue with and show the output of this command in the CMD: 'netsh wlan show interfaces' ",
            )
            self.supports_signal_strength = False
            # TODO Remove the signal strength topic for all the inets here !
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
            p = subprocess.run(["iwconfig", nic], capture_output=True, text=True)
            # p = cls.RunCommand(["iwconfig", nic]) # type hint return missing in subprocess.CompletedProcess
            if not bool(
                p.stdout
            ):  # if there is nothing in stdout for this nic it is no wireless interface
                continue
            for family in nicinfo:
                if family.family == AddressFamily.AF_INET:
                    nicip4 = family.address
                elif family.family == AddressFamily.AF_INET6:
                    nicip6 = family.address
                elif family.family == psutil.AF_LINK:
                    nicmac = family.address

            NIC_CHOICES.append(
                {
                    "name": WIFI_CHOICE_STRING.format(
                        nic,
                        nicip4 if nicip4 else nicip6,
                        nicmac,  # defaults to showing ipv4
                    ),
                    "value": nic,
                }
            )
        # TODO if no choices found AddEntry raises "no choices found"
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
