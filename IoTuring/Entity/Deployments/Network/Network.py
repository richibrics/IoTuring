from IoTuring.Entity.Entity import Entity
from IoTuring.Entity.EntityData import EntitySensor
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD # don't name Os as could be a problem with old configurations that used the Os entity

# Use cross-platform netifaces library for network interface details
try:
    import netifaces as ni
    library_available_netifaces = True
except Exception as e:
    library_available_netifaces = False

CONFIG_KEY_TITLE = "inet_name"
CONFIG_KEY_INCLUDE_IPV6 = "include_ipv6"

KEY_IPV4_ADDRESS = "IPv4_address"
KEY_IPV6_ADDRESS = "IPv6_address"

EXTRA_KEY_IP_ADDRESS = "IP Address"
EXTRA_KEY_MAC_ADDRESS = "MAC Address"
EXTRA_KEY_NETMASK = "Netmask"

EXTRA_KEY_BROADCAST = "Broadcast Address"
EXTRA_KEY_GATEWAY = "Gateway Address"

class Network(Entity):
    NAME = "Network"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.configured_inet = self.GetFromConfigurations(CONFIG_KEY_TITLE)
        self.include_ipv6 = self.GetTrueOrFalseFromConfigurations(CONFIG_KEY_INCLUDE_IPV6)

        self.RegisterEntitySensor(
            EntitySensor(
                self,
                KEY_IPV4_ADDRESS,
                supportsExtraAttributes=True
            )
        )

        if self.include_ipv6:
            self.RegisterEntitySensor(
                EntitySensor(
                    self,
                    KEY_IPV6_ADDRESS,
                    supportsExtraAttributes=True
                )
            )

    def Update(self):
        try:
            inet_addresses = ni.ifaddresses(self.configured_inet)

            ipv4 = {
                'ip_address': None,
                'netmask': None,
                'broadcast_address': None
            }
            ipv6 = {
                'ip_address': None,
                'netmask': None,
                'broadcast_address': None
            }
            mac_address = None

            if ni.AF_INET in inet_addresses:
                if len(inet_addresses[ni.AF_INET]) > 0:
                    # IPv4
                    if 'addr' in inet_addresses[ni.AF_INET][0]:
                        ipv4['ip_address'] = inet_addresses[ni.AF_INET][0]['addr']
                    if 'netmask' in inet_addresses[ni.AF_INET][0]:
                        ipv4['netmask'] = inet_addresses[ni.AF_INET][0]['netmask']
                    if 'broadcast' in inet_addresses[ni.AF_INET][0]:
                        ipv4['broadcast_address'] = inet_addresses[ni.AF_INET][0]['broadcast']

            if self.include_ipv6:
                if ni.AF_INET6 in inet_addresses:
                    if len(inet_addresses[ni.AF_INET6]) > 0:
                        # IPv6
                        if 'addr' in inet_addresses[ni.AF_INET6][0]:
                            ipv6['ip_address'] = inet_addresses[ni.AF_INET6][0]['addr']
                        if 'netmask' in inet_addresses[ni.AF_INET6][0]:
                            ipv6['netmask'] = inet_addresses[ni.AF_INET6][0]['netmask']
                        if 'broadcast' in inet_addresses[ni.AF_INET6][0]:
                            ipv6['broadcast_address'] = inet_addresses[ni.AF_INET6][0]['broadcast']

            if ni.AF_LINK in inet_addresses:
                if len(inet_addresses[ni.AF_LINK]) > 0:
                    # Link
                    mac_address = inet_addresses[ni.AF_LINK][0]['addr']

            self.SetEntitySensorValue(
                key = KEY_IPV4_ADDRESS,
                value = ipv4['ip_address'] if ipv4['ip_address'] is not None else "N/A"
            )

            if self.include_ipv6:
                self.SetEntitySensorValue(
                    key = KEY_IPV6_ADDRESS,
                    value = ipv6['ip_address']  if ipv4['ip_address'] is not None else "N/A"
                )

            for key, value in ipv4.items():
                if value is not None:
                    self.SetEntitySensorExtraAttribute(
                        sensorDataKey = KEY_IPV4_ADDRESS,
                        attributeKey = key,
                        attributeValue = str(value)
                    )

            if self.include_ipv6:
                for key, value in ipv4.items():
                    if value is not None:
                        self.SetEntitySensorExtraAttribute(
                            sensorDataKey = KEY_IPV4_ADDRESS,
                            attributeKey = key,
                            attributeValue = str(value)
                        )

            if mac_address is not None:
                self.SetEntitySensorExtraAttribute(
                    sensorDataKey = KEY_IPV4_ADDRESS,
                    attributeKey = "mac_address",
                    attributeValue = str(mac_address)
                )
                
                if self.include_ipv6:
                    self.SetEntitySensorExtraAttribute(
                        sensorDataKey = KEY_IPV6_ADDRESS,
                        attributeKey = "mac_address",
                        attributeValue = str(mac_address)
                    )

        except Exception as e:
            raise Exception(f"Error retrieving network information for interface '{self.configured_inet}': {str(e)}")

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        # Get the choices for menu:
        INET_AVAILABLE_INTERFACES = []

        for iface in ni.interfaces():
            INET_AVAILABLE_INTERFACES.append(
                {"name": iface, "value": iface}
            )

        preset = MenuPreset()
        preset.AddEntry(name="Network interface",
                        key=CONFIG_KEY_TITLE, mandatory=True,
                        question_type="select", choices=INET_AVAILABLE_INTERFACES)
        preset.AddEntry(name="Include IPv6 information",
                        key=CONFIG_KEY_INCLUDE_IPV6, mandatory=False,
                        question_type="yesno")
        return preset

    @classmethod
    def CheckSystemSupport(cls):
        if (not OsD.IsLinux() and not OsD.IsMacos() and not OsD.IsWindows()):
            raise cls.UnsupportedOsException()
        if (not library_available_netifaces):
            raise Exception("Error while importing netifaces library")