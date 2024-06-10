import re
from socket import AddressFamily

import psutil
import locale

from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

VALUEFORMATTEROPTIONS_DBM = ValueFormatterOptions(ValueFormatterOptions.TYPE_RADIOPOWER)
VALUEFORMATTEROPTIONS_PERCENTAGE = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_PERCENTAGE
)

WIFI_CHOICE_STRING = "Name: {:<15}, IP: {:<16}, MAC: {:<11}"

CONFIG_KEY_WIFI = "wifi"

SIGNAL_UNIT = "dBm"  # windows also supports "%"
SHOW_NA = False  # don't show not available extraAttributes

KEY_SIGNAL_STRENGTH_PERCENT = "signal_strength_percent"
KEY_SIGNAL_STRENGTH_DBM = "signal_strength_dbm"

# WINDOWS
EXTRA_KEY_NAME = "name"
EXTRA_KEY_DESCRIPTION = "description"
EXTRA_KEY_PHYSICAL_ADDRESS = "physical_address"
EXTRA_KEY_STATE = "state"
EXTRA_KEY_SSID = "ssid"
EXTRA_KEY_BSSID = "bssid"
EXTRA_KEY_NETWORK_TYPE = "network_type"
EXTRA_KEY_RADIO_TYPE = "radio_type"
EXTRA_KEY_SIGNAL = "signal"
EXTRA_KEY_PROFILE = "profile"
EXTRA_KEY_HOSTED_NETWORK_STATUS = "hosted_network_status"
# LINUX
# EXTRA_KEY_BSSID = "BSSID" # already in windows
# EXTRA_KEY_SSID = "ssid" # already in windows
EXTRA_KEY_FREQUENCY = "Frequency"
# EXTRA_KEY_RX_BYTES = "RX_bytes"
# EXTRA_KEY_TX_BYTES = "TX_bytes"
EXTRA_KEY_SIGNAL = "Signal"
# EXTRA_KEY_RX_BITRATE = "RX_bitrate"
# EXTRA_KEY_TX_BITRATE = "TX_bitrate"
# EXTRA_KEY_BSS_FLAGS = "BSS_flags"
# EXTRA_KEY_DTIM_PERIOD = "DTIM_period"
# EXTRA_KEY_BEACON_INTERVAL = "Beacon_interval"
# MACOS
EXTRA_KEY_AGRCTLRSSI = "agrCtlRSSI"
EXTRA_KEY_AGREXTRSSI = "agrExtRSSI"
# EXTRA_KEY_STATE = 'state' # already in windows
EXTRA_KEY_OP_MODE = "op mode"
EXTRA_KEY_LASTTXRATE = "lastTxRate"
EXTRA_KEY_MAXRATE = "maxRate"

# EXTRA_KEY_BSSID = 'BSSID' # already in windows
# EXTRA_KEY_SSID = 'SSID' # already in windows
# EXTRA_KEY_CHANNEL = 'channel' # already in windows


class Wifi(Entity):
    NAME = "Wifi"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.platform = OsD.GetOs()
        self.locale_str, _ = locale.getdefaultlocale()
        self.language: str = self.locale_str.split("_")[0]
        self.showNA = SHOW_NA

        # In macos trick the language to be english since the output of airport is always in english
        if OsD.IsMacos():
            self.language = "en"

        self.wifiInterface = self.GetFromConfigurations(CONFIG_KEY_WIFI)

        self.commands = {
            OsD.WINDOWS: ["netsh", "wlan", "show", "interfaces"],
            OsD.LINUX: ["iw", "dev", self.wifiInterface, "link"],
            OsD.MACOS: [
                "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                "-I",
            ],
        }
        self.patterns = {
            OsD.WINDOWS: {
                #"en": {
                    "Description": r"Description\s+:\s+(.*)",
                    "Physical address": r"Physical address\s+:\s+([\w:]+)",
                    "State": r"State\s+:\s+(.*)",
                    "SSID": r"SSID\s+:\s+(.*)",
                    "BSSID": r"BSSID\s+:\s+([\w:]+)",
                    "Network type": r"Network type\s+:\s+(.*)",
                    "Radio type": r"Radio type\s+:\s+(.*)",
                    "Signal": r"Signal\s+:\s+(\d+%?)",
                    "Profile": r"Profile\s+:\s+(.*)",
                    "Hosted network status": r"Hosted network status\s+:\s+(.*)",
                },
                #"de": {
                #    "Schnittstellenname": r"Schnittstellenname:\s+(.+)",
                #    "Beschreibung": r"Beschreibung:\s+(.+)",
                #    "Physische Adresse": r"Physische Adresse:\s+([0-9A-Fa-f-]+)",
                #    "Status": r"Status:\s+(.+)",
                #    "SSID": r"SSID:\s+(.+)",
                #    "BSSID": r"BSSID:\s+([0-9A-Fa-f-]+)",
                #    "Netzwerktyp": r"Netzwerktyp:\s+(.+)",
                #    "Funktyp": r"Funktyp:\s+(.+)",
                #    "Signal": r"Signal:\s+(\d+%?)",
                #    "Profil": r"Profil:\s+(.+)",
                #},
                #"sp": {
                #    "Nombre de interfaz": r"Nombre de interfaz:\s+(.+)",
                #    "Descripción": r"Descripción:\s+(.+)",
                #    "Dirección física": r"Dirección física:\s+([0-9A-Fa-f-]+)",
                #    "Estado": r"Estado:\s+(.+)",
                #    "SSID": r"SSID:\s+(.+)",
                #    "BSSID": r"BSSID:\s+([0-9A-Fa-f-]+)",
                #    "Tipo de red": r"Tipo de red:\s+(.+)",
                #    "Señal": r"Señal:\s+(\d+%?)",
                #    "Perfil": r"Perfil:\s+(.+)",
                #},
            #},
            OsD.LINUX: {
                "BSSID": r'Connected to (\S+) \(on \S+\)',
                "SSID": r'SSID: (.+)',
                "Frequency": r'freq: ([\d.]+)',
                #"RX_bytes": r'RX: (\d+) bytes \(\d+ packets\)',
                #"TX_bytes": r'TX: (\d+) bytes \(\d+ packets\)',
                "Signal": r'signal: (-?\d+) dBm',
                #"RX_bitrate": r'rx bitrate: ([\d.]+) MBit/s',
                #"TX_bitrate": r'tx bitrate: ([\d.]+) MBit/s',
                #"BSS_flags": r'bss flags: (.+)',
                #"DTIM_period": r'dtim period: (\d+)',
                #"Beacon_interval": r'beacon int: (\d+)'
            },
            OsD.MACOS: {  # no language differentiation in macos: always english
                "agrCtlRSSI": r"[^\n][\s]*agrCtlRSSI:\s+(-?\d+)\n",
                "agrExtRSSI": r"[^\n][\s]*agrExtRSSI:\s+(-?\d+)\n",
                "state": r"[^\n][\s]*state:\s+(\w+)\n",
                "op mode": r"[^\n][\s]*op mode:\s+(\w+)\n",
                "lastTxRate": r"[^\n][\s]*lastTxRate:\s+(\d+)\n",
                "maxRate": r"[^\n][\s]*maxRate:\s+(\d+)\n",
                "BSSID": r"[^\n][\s]*BSSID:\s+([\w:]+)\n",
                "SSID": r"\n[\s]*SSID:\s+([\w\s]+)\n",
                "channel": r"[^\n][\s]*channel:\s+([\d,]+)\n",
            },
        }

        if OsD.IsWindows():
            self.keySignalStrength = KEY_SIGNAL_STRENGTH_PERCENT
            self.valueFormatterOptionsSignalStrength = VALUEFORMATTEROPTIONS_PERCENTAGE
        else:
            self.keySignalStrength = KEY_SIGNAL_STRENGTH_DBM
            self.valueFormatterOptionsSignalStrength = VALUEFORMATTEROPTIONS_DBM

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                key=self.keySignalStrength,
                supportsExtraAttributes=True,
                valueFormatterOptions=self.valueFormatterOptionsSignalStrength,
            ),
        )

    def Update(self):
        p = self.RunCommand(self.commands[self.platform])
        if not p.stdout:
            raise Exception("error in GetWirelessInfo\n", p.stderr)
        wifiInfo = self.GetWirelessInfo(p.stdout)
        if not wifiInfo:
            raise Exception("error while parsing wirelessInfo")
        # set signal strength
        if self.platform == OsD.WINDOWS and "Signal" in wifiInfo:
            if SIGNAL_UNIT == "%":
                self.SetEntitySensorValue(
                    key=self.keySignalStrength, value=wifiInfo["Signal"]
                )
            elif SIGNAL_UNIT == "dBm":
                self.SetEntitySensorValue(
                    key=self.keySignalStrength,
                    value=self.PercentToDbm(int(wifiInfo["Signal"][:-1])),
                )
        elif self.platform == OsD.LINUX and "Signal" in wifiInfo:
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["Signal"]
            )
        elif self.platform == OsD.MACOS and "agrCtlRSSI" in wifiInfo:
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["agrCtlRSSI"]
            )
        else:  # if there is no signal level found the interface might not be connected to an access point
            self.SetEntitySensorValue(key=self.keySignalStrength, value="not connected")

        # Extra attributes
        for key in self.patterns[self.platform]:
            extraKey = "EXTRA_KEY_" + key.upper().replace(" ", "_").replace(".", "_")
            if key in wifiInfo:
                attributevalue = wifiInfo[key]
            elif self.showNA:
                attributevalue = "not available"
            else:
                continue

            self.SetEntitySensorExtraAttribute(
                sensorDataKey=self.keySignalStrength,
                attributeKey=globals()[extraKey],
                attributeValue=attributevalue,
            )

    def GetWirelessInfo(self, stdout):
        wifi_info = {}
        for key, pattern in self.patterns[self.platform].items():
            match = re.search(pattern, stdout, re.IGNORECASE)
            if match:
                wifi_info[key] = match.group(1) if match.group(1) else match.group(0)
        return wifi_info

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        NIC_CHOICES = Wifi.GetWifiNics(getInfo=True)
        SIGNAL_CHOICES = ["%", "dBm"]

        preset = MenuPreset()
        preset.AddEntry(
            name="Interface to check",
            key=CONFIG_KEY_WIFI,
            mandatory=True,
            question_type="select",
            choices=NIC_CHOICES,
        )
        if OsD.IsWindows():
            preset.AddEntry(
                name="Signal Quality in dBm or percent",
                key=SIGNAL_UNIT,
                mandatory=True,
                question_type="select",
                choices=SIGNAL_CHOICES,
            )
        return preset

    @staticmethod
    def PercentToDbm(percentage):
        return (percentage / 2) - 100

    @staticmethod
    def GetWifiNics(getInfo=True):
        interfaces = psutil.net_if_addrs()
        NIC_CHOICES = []

        def appendNicChoice(interfaceName, nicip4="", nicip6="", nicmac=""):
            NIC_CHOICES.append(
                {
                    "name": WIFI_CHOICE_STRING.format(
                        interfaceName,
                        nicip4 if nicip4 else nicip6,  # defaults to showing ipv4
                        nicmac,
                    ),
                    "value": interfaceName,
                }
            )

        ip4 = ""
        ip6 = ""
        mac = ""

        if OsD.IsLinux():
            for interface in interfaces:
                p = OsD.RunCommand(["iw", "dev", interface, "link"])
                if (
                    p.returncode > 0
                ):  # if the returncode is 0 iwconfig succeeded, else continue with next interface
                    continue
                if not getInfo:
                    appendNicChoice(interface)
                    continue
                else:
                    nicinfo = interfaces[interface]  # TODO Typehint
                    for nicaddr in nicinfo:
                        if nicaddr.family == AddressFamily.AF_INET:
                            ip4 = nicaddr.address
                            continue
                        elif nicaddr.family == AddressFamily.AF_INET6:
                            ip6 = nicaddr.address
                            continue
                        elif nicaddr.family == psutil.AF_LINK:
                            mac = nicaddr.address
                            continue
                appendNicChoice(interface, ip4, ip6, mac)
            return NIC_CHOICES

        elif OsD.IsWindows():
            p = OsD.RunCommand(["netsh", "wlan", "show", "interfaces"])
            if (
                p.returncode > 0
            ):  # if the returncode is 0 iwconfig succeeded, else continue with next interface
                raise Exception("RunCommand netsh returncode > 0")
            output = p.stdout
            numInterfacesMatch = re.search(
                r"There is (\d+) interface(?:s)? on the system", output
            )
            numOfInterfaces = int(numInterfacesMatch.group(1))
            if numOfInterfaces == 0:
                raise Exception("no wireless interface found")
            elif numOfInterfaces > 1:
                raise Exception(
                    "more than one wireless interface not supported, create a github issue with the output of 'netsh wlan show interfaces' atached"
                )
            interfaceMatch = re.search(r"Name\s+:\s+(\w+)", output)
            interfaceName = interfaceMatch.group(1)
            if not getInfo:
                appendNicChoice(interfaceName)
            else:
                nicinfo = interfaces[interfaceName]  # TODO Typehint
                for nicaddr in nicinfo:
                    if nicaddr.family == AddressFamily.AF_INET:
                        ip4 = nicaddr.address
                        continue
                    elif nicaddr.family == AddressFamily.AF_INET6:
                        ip6 = nicaddr.address
                        continue
                    elif nicaddr.family == psutil.AF_LINK:
                        mac = nicaddr.address
                        continue
                appendNicChoice(interfaceName, ip4, ip6, mac)
            return NIC_CHOICES

        elif OsD.IsMacos():
            for interface in interfaces:
                p = OsD.RunCommand(["airport", interface])
                if (
                    p.returncode > 0
                ):  # if the returncode is 0 iwconfig succeeded, else continue with next interface
                    continue
                nicinfo = interfaces[interface]  # TODO Typehint
                if not getInfo:
                    appendNicChoice(interface)
                    continue
                else:
                    for nicaddr in nicinfo:
                        if nicaddr.family == AddressFamily.AF_INET:
                            ip4 = nicaddr.address
                            continue
                        elif nicaddr.family == AddressFamily.AF_INET6:
                            ip6 = nicaddr.address
                            continue
                        elif nicaddr.family == psutil.AF_LINK:
                            mac = nicaddr.address
                            continue

                appendNicChoice(interface, ip4, ip6, mac)
            return NIC_CHOICES

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            if not OsD.CommandExists("iw"):
                raise Exception("iw not found")
            wifiNics = Wifi.GetWifiNics(getInfo=False)
            if not wifiNics:
                raise Exception("no wireless interface found")

        elif OsD.IsWindows():
            if not OsD.CommandExists("netsh"):
                raise Exception("netsh not found")
            elif "English" not in locale.getlocale()[0]:
                raise Exception(
                    "locale not supported, create a github issue with the output of 'netsh wlan show interfaces' atached"
                )
            wifiNics = Wifi.GetWifiNics(getInfo=False)
            if not wifiNics:
                raise Exception("no wireless interface found")

        elif OsD.IsMacos():
            if not OsD.CommandExists("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"):
                raise Exception("airport not found")
            wifiNics = Wifi.GetWifiNics(getInfo=False)
            if not wifiNics:
                raise Exception("no wireless interface found")

        else:
            raise Exception("OS detection failed")
