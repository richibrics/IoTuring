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
VALUEFORMATTEROPTIONS_PERCENTAGE = ValueFormatterOptions(ValueFormatterOptions.TYPE_PERCENTAGE)
WIFI_CHOICE_STRING = "Name: {:<15}, IP: {:<16}, MAC: {:<11}"

CONFIG_KEY_WIFI = "wifi"
CONFIG_KEY_SHOW_NA = "show_na"

KEY_SIGNAL_STRENGTH_PERCENT = "signal_strength_percent"
KEY_SIGNAL_STRENGTH_DBM = "signal_strength_dbm"
# WINDOWS
EXTRA_KEY_NAME = "name"
EXTRA_KEY_DESCRIPTION = "description"
EXTRA_KEY_GUID = "guid"
EXTRA_KEY_PHYSICAL_ADDRESS = "physical_address"
EXTRA_KEY_STATE = "state"
EXTRA_KEY_SSID = "ssid"
EXTRA_KEY_BSSID = "bssid"
EXTRA_KEY_NETWORK_TYPE = "network_type"
EXTRA_KEY_RADIO_TYPE = "radio_type"
EXTRA_KEY_AUTHENTICATION = "authentication"
EXTRA_KEY_CIPHER = "cipher"
EXTRA_KEY_CONNECTION_MODE = "connection_mode"
EXTRA_KEY_CHANNEL = "channel"
EXTRA_KEY_RECEIVE_RATE = "receive_rate"
EXTRA_KEY_TRANSMIT_RATE = "transmit_rate"
EXTRA_KEY_SIGNAL = "signal"
EXTRA_KEY_PROFILE = "profile"
EXTRA_KEY_HOSTED_NETWORK_STATUS = "hosted_network_status"
# LINUX
EXTRA_KEY_ESSID = "ESSID"
EXTRA_KEY_MODE = "Mode"
EXTRA_KEY_FREQUENCY = "Frequency"
EXTRA_KEY_ACCESS_POINT = "Access_Point"
EXTRA_KEY_BIT_RATE = "Bit_Rate"
EXTRA_KEY_TX_POWER = "Tx_Power"
EXTRA_KEY_LINK_QUALITY = "Link_Quality"
EXTRA_KEY_SIGNAL_LEVEL = "Signal_Level"
EXTRA_KEY_RX_INVALID_NWID = "Rx_invalid_nwid"
EXTRA_KEY_RX_INVALID_CRYPT = "Rx_invalid_crypt"
EXTRA_KEY_RX_INVALID_FRAG = "Rx_invalid_frag"
EXTRA_KEY_TX_EXCESSIVE_RETRIES = "Tx_excessive_retries"
EXTRA_KEY_INVALID_MISC = "Invalid_misc"
EXTRA_KEY_MISSED_BEACON = "Missed_beacon"
# MACOS
EXTRA_KEY_AGRCTLRSSI = "agrCtlRSSI"
EXTRA_KEY_AGREXTRSSI = "agrExtRSSI"
EXTRA_KEY_AGRCTLNOISE = "agrCtlNoise"
EXTRA_KEY_AGREXTNOISE = "agrExtNoise"
# EXTRA_KEY_STATE = 'state' # already in windows
EXTRA_KEY_OP_MODE = "op mode"
EXTRA_KEY_LASTTXRATE = "lastTxRate"
EXTRA_KEY_MAXRATE = "maxRate"
EXTRA_KEY_LASTASSOCSTATUS = "lastAssocStatus"
EXTRA_KEY_802_11_AUTH = "802.11 auth"
EXTRA_KEY_LINK_AUTH = "link auth"
# EXTRA_KEY_BSSID = 'BSSID' # already in windows
# EXTRA_KEY_SSID = 'SSID' # already in windows
EXTRA_KEY_MCS = "MCS"
# EXTRA_KEY_CHANNEL = 'channel' # already in windows


class Wifi(Entity):
    NAME = "Wifi"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.wifiInterface = self.GetFromConfigurations(CONFIG_KEY_WIFI)
        self.showNA = True if self.GetFromConfigurations(CONFIG_KEY_SHOW_NA) == "Y" else False

        self.commands = {
            OsD.WINDOWS: ["netsh", "wlan", "show", "interfaces"],
            OsD.LINUX: ["iwconfig", self.wifiInterface],
            OsD.MACOS: ["airport", "I"],
        }
        self.patterns = {
            OsD.WINDOWS: {
                "en": {
                    "Description": r"Description\s+:\s+(.*)",
                    "GUID": r"GUID\s+:\s+([\w-]+)",
                    "Physical address": r"Physical address\s+:\s+([\w:]+)",
                    "State": r"State\s+:\s+(.*)",
                    "SSID": r"SSID\s+:\s+(.*)",
                    "BSSID": r"BSSID\s+:\s+([\w:]+)",
                    "Network type": r"Network type\s+:\s+(.*)",
                    "Radio type": r"Radio type\s+:\s+(.*)",
                    "Authentication": r"Authentication\s+:\s+(.*)",
                    "Cipher": r"Cipher\s+:\s+(.*)",
                    "Connection mode": r"Connection mode\s+:\s+(.*)",
                    "Channel": r"Channel\s+:\s+(\d+)",
                    "Receive rate": r"Receive rate \(Mbps\)\s+:\s+([\d.]+)",
                    "Transmit rate": r"Transmit rate \(Mbps\)\s+:\s+([\d.]+)",
                    "Signal": r"Signal\s+:\s+(\d+%?)",
                    "Profile": r"Profile\s+:\s+(.*)",
                    "Hosted network status": r"Hosted network status\s+:\s+(.*)",
                },
                "de": {
                    "Schnittstellenname": r"Schnittstellenname:\s+(.+)",
                    "Beschreibung": r"Beschreibung:\s+(.+)",
                    "Physische Adresse": r"Physische Adresse:\s+([0-9A-Fa-f-]+)",
                    "Status": r"Status:\s+(.+)",
                    "SSID": r"SSID:\s+(.+)",
                    "BSSID": r"BSSID:\s+([0-9A-Fa-f-]+)",
                    "Netzwerktyp": r"Netzwerktyp:\s+(.+)",
                    "Funktyp": r"Funktyp:\s+(.+)",
                    "Authentifizierung": r"Authentifizierung:\s+(.+)",
                    "Verschlüsselung": r"Verschlüsselung:\s+(.+)",
                    "Verbindungsmodus": r"Verbindungsmodus:\s+(.+)",
                    "Kanal": r"Kanal:\s+(\d+)",
                    "Empfangsrate (Mbps)": r"Empfangsrate \(Mbps\):\s+([\d.]+)",
                    "Übertragungsrate (Mbps)": r"Übertragungsrate \(Mbps\):\s+([\d.]+)",
                    "Signal": r"Signal:\s+(\d+%?)",
                    "Profil": r"Profil:\s+(.+)"
                },
                "sp": {
                    "Nombre de interfaz": r"Nombre de interfaz:\s+(.+)",
                    "Descripción": r"Descripción:\s+(.+)",
                    "Dirección física": r"Dirección física:\s+([0-9A-Fa-f-]+)",
                    "Estado": r"Estado:\s+(.+)",
                    "SSID": r"SSID:\s+(.+)",
                    "BSSID": r"BSSID:\s+([0-9A-Fa-f-]+)",
                    "Tipo de red": r"Tipo de red:\s+(.+)",
                    "Tipo de radio": r"Tipo de radio:\s+(.+)",
                    "Autenticación": r"Autenticación:\s+(.+)",
                    "Cifrado": r"Cifrado:\s+(.+)",
                    "Modo de conexión": r"Modo de conexión:\s+(.+)",
                    "Canal": r"Canal:\s+(\d+)",
                    "Velocidad de recepción (Mbps)": r"Velocidad de recepción \(Mbps\):\s+([\d.]+)",
                    "Velocidad de transmisión (Mbps)": r"Velocidad de transmisión \(Mbps\):\s+([\d.]+)",
                    "Señal": r"Señal:\s+(\d+%?)",
                    "Perfil": r"Perfil:\s+(.+)"
                }
            },
            OsD.LINUX: {
                "en" : { 
                    "ESSID": r'ESSID:"([^"]*)"',
                    "Mode": r"Mode:([^\s]+)",
                    "Frequency": r"Frequency:([\d.]+) (GHz|Mhz)",
                    "Access_Point": r"Access Point: ([\w:]+)",
                    "Bit_Rate": r"Bit Rate=([\d.]+) (\w+/s)",
                    "Tx_Power": r"Tx-Power=(-?\d+) (\w+)",
                    "Link_Quality": r"Link Quality=(\d+/\d+)",
                    "Signal_Level": r"Signal level=(-?\d+) (\w+)",
                    "Rx_invalid_nwid": r"Rx invalid nwid:(\d+)",
                    "Rx_invalid_crypt": r"Rx invalid crypt:(\d+)",
                    "Rx_invalid_frag": r"Rx invalid frag:(\d+)",
                    "Tx_excessive_retries": r"Tx excessive retries:(\d+)",
                    "Invalid_misc": r"Invalid misc:(\d+)",
                    "Missed_beacon": r"Missed beacon:(\d+)",
                },
            },
            OsD.MACOS: {
                "en": {
                "agrCtlRSSI": r"agrCtlRSSI:\s+(-?\d+)",
                "agrExtRSSI": r"agrExtRSSI:\s+(-?\d+)",
                "agrCtlNoise": r"agrCtlNoise:\s+(-?\d+)",
                "agrExtNoise": r"agrExtNoise:\s+(-?\d+)",
                "state": r"state:\s+(\w+)",
                "op mode": r"op mode:\s+(\w+)",
                "lastTxRate": r"lastTxRate:\s+(\d+)",
                "maxRate": r"maxRate:\s+(\d+)",
                "lastAssocStatus": r"lastAssocStatus:\s+(\d+)",
                "802.11 auth": r"802\.11 auth:\s+(\w+)",
                "link auth": r"link auth:\s+(\w+-\w+)",
                "BSSID": r"BSSID:\s+([\w:]+)",
                "SSID": r"SSID:\s+([\w\s]+)",
                "MCS": r"MCS:\s+(\d+)",
                "channel": r"channel:\s+([\d,]+)",
                }
            },
        }
        self.platform = OsD.GetOs()
        self.locale_str, _ = locale.getlocale()
        self.language: str = self.locale_str.split("_")[0]


        if self.platform == OsD.WINDOWS:
            self.keySignalStrength = KEY_SIGNAL_STRENGTH_PERCENT
            self.valueFormatterOptionsSignalStrength =  VALUEFORMATTEROPTIONS_PERCENTAGE
        else:
            self.keySignalStrength = KEY_SIGNAL_STRENGTH_DBM
            self.valueFormatterOptionsSignalStrength = VALUEFORMATTEROPTIONS_DBM

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                self.keySignalStrength,
                supportsExtraAttributes=True,
                valueFormatterOptions=VALUEFORMATTEROPTIONS_PERCENTAGE if self.platform == OsD.WINDOWS else VALUEFORMATTEROPTIONS_DBM
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
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["Signal"]
            )
        elif self.platform == OsD.LINUX and "Signal_Level" in wifiInfo:
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["Signal_Level"]
            )
        elif self.platform == OsD.MACOS and "agrCtlRSSI" in wifiInfo: 
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["agrCtlRSSI"]
            )
        else:  # if there is no signal level found the interface might not be connected to an access point
            self.SetEntitySensorValue(key=self.keySignalStrength, value="not connected")
        for key in self.patterns[self.platform][self.language]:
            extraKey = "EXTRA_KEY_" + key.upper().replace(" ", "_")
            if key in wifiInfo:
                attributevalue = wifiInfo[key] 
            elif self.showNA:
                attributevalue = "not available"
            else: 
                continue
            
            self.SetEntitySensorExtraAttribute(
                sensorDataKey=self.keySignalStrength,
                attributeKey=globals()[extraKey],
                attributeValue=attributevalue
            )

    def GetWirelessInfo(self, stdout):
        wifi_info = {}
        for key, pattern in self.patterns[self.platform][self.language].items():
            match = re.search(pattern, stdout, re.IGNORECASE)
            if match:
                wifi_info[key] = match.group(1) if match.group(1) else match.group(0)
        return wifi_info

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        NIC_CHOICES = Wifi.GetWifiNics(getInfo=True)

        preset = MenuPreset()
        preset.AddEntry(
            name="Interface to check",
            key=CONFIG_KEY_WIFI,
            mandatory=True,
            question_type="select",
            choices=NIC_CHOICES,
        )
        preset.AddEntry(
            name="if attribute is not available, show it",
            key=CONFIG_KEY_SHOW_NA,
            mandatory=False,
            question_type="yesno",
        )
        return preset

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
                p = OsD.RunCommand(["iwconfig", interface])
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
                appendNicChoice(interface)
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
                    appendNicChoice(interface, ip4, ip6, mac)
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
            if not OsD.CommandExists("iwconfig"):
                raise Exception("iwconfig not found")
            wifiNics = Wifi.GetWifiNics(getInfo=False)
            if not wifiNics:
                raise Exception("no wireless interface found")

        elif OsD.IsWindows():
            if not OsD.CommandExists("netsh"):
                raise Exception("netsh not found")
            elif "English" not in locale.getlocale():
                raise Exception(
                    "locale not supported, create a github issue with the output of 'netsh wlan show interfaces' atached"
                )
            wifiNics = Wifi.GetWifiNics(getInfo=False)
            if not wifiNics:
                raise Exception("no wireless interface found")

        elif OsD.IsMacos():
            if not OsD.CommandExists("airport"):
                raise Exception("airport not found")
            wifiNics = Wifi.GetWifiNics(getInfo=False)
            if not wifiNics:
                raise Exception("no wireless interface found")

        else:
            raise Exception("OS detection failed")
