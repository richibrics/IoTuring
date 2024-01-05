import re
from socket import AddressFamily

import psutil
import locale

from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Entity.ValueFormat import ValueFormatterOptions
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD

VALUEFORMATTEROPTIONS_MBPS = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_BIT_PER_SECOND, adjust_size="Mbps"
)
valueFormatterOptions = ValueFormatterOptions(ValueFormatterOptions.TYPE_RADIOPOWER)
WIFI_CHOICE_STRING = "Name: {:<15}, IP: {:<16}, MAC: {:<11}"

CONFIG_KEY_WIFI = "wifi"
NIC_CHOICES = []

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

        self.commands = {
            OsD.WINDOWS: ["netsh", "wlan", "show", "interfaces"],
            OsD.LINUX: ["iwconfig", self.wifiInterface],
            OsD.MACOS: ["airport", "I"],
        }
        self.patterns = {
            OsD.WINDOWS: {
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
            OsD.LINUX: {
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
            OsD.MACOS: {
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
            },
        }
        self.platform = OsD.GetOs()
        if (
            self.platform == OsD.WINDOWS
        ):  # Windows shows signal stgrength in percent Unix Systems in dbm
            self.keySignalStrength = KEY_SIGNAL_STRENGTH_PERCENT
        else:
            self.keySignalStrength = KEY_SIGNAL_STRENGTH_DBM

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                self.keySignalStrength,
                supportsExtraAttributes=True,
                valueFormatterOptions=ValueFormatterOptions(
                    ValueFormatterOptions.TYPE_RADIOPOWER
                ),
            )
        )

    def Update(self):
        p = self.RunCommand(self.commands[self.platform])
        if not p.stdout:
            raise Exception("error in GetWirelessInfo\n", p.stderr)
        wifiInfo = self.GetWirelessInfo(p.stdout)
        if not wifiInfo:
            raise Exception("error while parsing wirelessInfo")
        # set signal strength
        if "Signal" in wifiInfo:  # Windows
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["Signal"]
            )
        elif "Signal_Level" in wifiInfo:  # Linux
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["Signal_Level"]
            )
        elif "agrCtlRSSI" in wifiInfo:
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value=wifiInfo["agrCtlRSSI"]
            )
        else: # if there is no signal level found the interface might not be connected to an access point
            self.SetEntitySensorValue(
                key=self.keySignalStrength, value="not connected"
            )
        for key in self.patterns[self.platform]:
            extraKey = "EXTRA_KEY_" + key.upper().replace(" ", "_")
            self.SetEntitySensorExtraAttribute(
                sensorDataKey=self.keySignalStrength,
                attributeKey=globals()[extraKey],
                attributeValue=wifiInfo[key] if key in wifiInfo else "not available",
            )

    def GetWirelessInfo(self, stdout):
        wifi_info = {}
        for key, pattern in self.patterns[self.platform].items():
            match = re.search(pattern, stdout, re.IGNORECASE)
            if match:
                wifi_info[key] = match.group(1) if match.group(1) else match.group(0)

        self.Log(self.LOG_DEBUG, wifi_info)
        return wifi_info

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:         

        preset = MenuPreset()
        preset.AddEntry(
            name="Interface to check",
            key=CONFIG_KEY_WIFI,
            mandatory=True,
            question_type="select",
            choices=NIC_CHOICES
        )
        return preset

    @classmethod
    def CheckSystemSupport(cls):

        def appendNicChoice(interfaceName, nicip4 = "", nicip6 = "", nicmac = ""):
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
        interfaces = psutil.net_if_addrs()

        if OsD.IsLinux():
            if not OsD.CommandExists("iwconfig"):
                raise Exception("iwconfig not found")
            
            for interface in interfaces:
                p = OsD.RunCommand(["iwconfig", interface])
                if p.returncode > 0: # if the returncode is 0 iwconfig succeeded, else continue with next interface
                    continue
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

        elif OsD.IsWindows():
            if not OsD.CommandExists("netsh"):
                raise Exception("netsh not found")
            elif "English" not in locale.getlocale():
                raise Exception("locale not supported, create a github issue with the output of 'netsh wlan show interfaces' atached")
            
            p = OsD.RunCommand(["netsh", "wlan", "show", "interfaces"])
            if p.returncode > 0: # if the returncode is 0 iwconfig succeeded, else continue with next interface
                continue
            output = p.stdout
            numInterfacesMatch = re.search(r"There is (\d+) interface(?:s)? on the system", output)
            numOfInterfaces = int(numInterfacesMatch.group(1))
            if numOfInterfaces == 0:
                raise Exception("no wireless interface found")
            elif numOfInterfaces > 1:
                raise Exception("more than one wireless interface not supported, create a github issue with the output of 'netsh wlan show interfaces' atached")
            interfaceMatch = re.search(r"Name\s+:\s+(\w+)", output)
            interfaceName = interfaceMatch.group(1)
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

            
            

        elif OsD.IsMacos(): 
            if not OsD.CommandExists("airport"):
                raise Exception("airport not found")
            for interface in interfaces: # TODO Test this code is mostly yolo'ed the linux way but with airport
                    p = OsD.RunCommand(["airport", interface])
                    if p.returncode > 0: # if the returncode is 0 iwconfig succeeded, else continue with next interface
                        continue
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

        else:
            raise Exception("OS detection failed")
