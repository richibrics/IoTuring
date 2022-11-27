# Wireless strenght method taken from: https://github.com/s7jones/Wifi-Signal-Plotter/

import psutil
import re
import subprocess

from IoTuring.Entity.Entity import Entity 
from ValueFormatter import ValueFormatter

supports_win_signal_strenght = True
supports_linux_signal_strenght = True 
supports_macos_signal_strenght = False # to avoid using those data in macOS

try:
    import winreg
except:
    supports_win_signal_strenght = False

try:
    import netifaces
except:
    supports_linux_signal_strenght = False


DOWNLOAD_TRAFFIC_TOPIC = 'network/traffic/bytes_recv'
UPLOAD_TRAFFIC_TOPIC = 'network/traffic/bytes_sent'

NIC_ADDRESS_TOPIC = 'network/interfaces/{}/private_address' # nic name in brackets
NIC_SIGNAL_STRENGHT_TOPIC = 'network/interfaces/{}/signal_strenght' # nic name in brackets - 0 for non wireless nic

# Supports FORMATTED for traffic information

SIZE_OPTION_KEY = "size"
EXCLUDE_INTERFACES_CONTENT_OPTION_KEY = "exclude_interfaces"
RENAME_INTERFACES_CONTENT_OPTION_KEY = "rename_interfaces"

NIC_PRIVATE_ADDRESS_DISCOVERY_NAME_FORMAT = "{} private ip"
NIC_PRIVATE_ADDRESS_DISCOVERY_ICON = "mdi:ip-network"

NIC_SIGNAL_STRENGHT_DISCOVERY_NAME_FORMAT = "{} signal strenght"
NIC_SIGNAL_STRENGHT_DISCOVERY_ICON = "mdi:network-strength-3"

# Windows returns strenght in %, linux in dB
NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT_LINUX = "dB"
NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT_WINDOWS = "%"

class Network(Entity):
    def Initialize(self):
        
        self.supports_signal_strenght = True

        # Get list of interfaces to ignore: if not specified: [], if set only a string: [string], if set a list: [item1,item2] -> I always have a list (else schema not validated)
        self.excludeInterfaces=self.Configurator.ReturnAsList(self.GetOption([self.consts.CONTENTS_OPTION_KEY,EXCLUDE_INTERFACES_CONTENT_OPTION_KEY],[]))


        # Interfaces
        self.nics = []
        for nic in netifaces.interfaces():
            # If I don't exclude it and if has a private address (AF_INET=2)
            if '{' not in self.GetNicName(nic) and self.GetNicName(nic) not in self.excludeInterfaces and netifaces.AF_INET in netifaces.ifaddresses(nic):
                self.AddTopic(self.InterfaceTopicFormat(NIC_ADDRESS_TOPIC,self.GetNicName(nic)))
                self.AddTopic(self.InterfaceTopicFormat(NIC_SIGNAL_STRENGHT_TOPIC,self.GetNicName(nic)))
                self.nics.append(nic)
                self.Log(self.Logger.LOG_DEBUG, "Added " + self.GetNicName(nic,getRenamed=False)+ " interface")
                if self.GetNicName(nic) != self.GetNicName(nic, getRenamed= False):
                    self.Log(self.Logger.LOG_DEBUG, "Renamed " + self.GetNicName(nic,getRenamed=False)+ " to " + self.GetNicName(nic))

        # Traffic data
        self.AddTopic(DOWNLOAD_TRAFFIC_TOPIC)
        self.AddTopic(UPLOAD_TRAFFIC_TOPIC)


    def PostInitialize(self):
        global supports_linux_signal_strenght,supports_win_signal_strenght,supports_macos_signal_strenght

        os = self.GetOS()
    
        self.UpdateWirelessSignalStrenghtSpecificFunction = None   # Specific function for this os/de, set this here to avoid all if else except at each update

        if(os == self.consts.FIXED_VALUE_OS_WINDOWS):    
            self.NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT= NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT_WINDOWS
            self.UpdateWirelessSignalStrenghtSpecificFunction = self.GetWirelessStrenght_Windows
        
            if not supports_win_signal_strenght:
                self.Log(self.Logger.LOG_ERROR,"Error with signal strenght sensor, have you installed all the dependencies ? (winreg, netifaces)")
                # If not supported, I remove the signal strenght topic (also discovery won't include anymore this topic)
                self.RemoveSignalStrenghtTopics()
                self.supports_signal_strenght = False

        elif(os ==  self.consts.FIXED_VALUE_OS_LINUX):
            self.NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT= NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT_LINUX
            self.UpdateWirelessSignalStrenghtSpecificFunction = self.GetWirelessStrenght_Linux

            if not supports_linux_signal_strenght:
                self.Log(self.Logger.LOG_ERROR,"Error with signal strenght sensor, have you installed all the dependencies ? (netifaces)")
                # If not supported, I remove the signal strenght topic (also discovery won't include anymore this topic)
                self.RemoveSignalStrenghtTopics()
                self.supports_signal_strenght = False


        # elif(Get_Operating_System() ==  self.consts.FIXED_VALUE_OS_MACOS):
        #    self.UpdateSpecificFunction =  NOT SUPPORTED
        
        else:
            self.Log(self.Logger.LOG_ERROR, 'No wireless signal strenght sensor available for this operating system')
            # If not supported, I remove the signal strenght topic (also discovery won't include anymore this topic)
            self.RemoveSignalStrenghtTopics()
            self.supports_signal_strenght = False

        


    def Update(self):
        # Interfaces data
        strenght_data = self.UpdateWirelessSignalStrenghtSpecificFunction()
        strenght_set = False # If after the check in the strenght data values, if the nic hasn't a value, set 0
        
        for nic in self.nics:
            # Private address
            self.SetTopicValue(self.InterfaceTopicFormat(NIC_ADDRESS_TOPIC,self.GetNicName(nic)), netifaces.ifaddresses(nic)[netifaces.AF_INET][0]['addr'])
            
            # Wireless strenght 
            if self.supports_signal_strenght:
                strenght_set = False
                for nic_strenght in strenght_data:
                    if nic_strenght[0]==self.GetNicName(nic,getRenamed=False):
                        strenght_set = True
                        self.SetTopicValue(self.InterfaceTopicFormat(NIC_SIGNAL_STRENGHT_TOPIC,self.GetNicName(nic)), nic_strenght[1])
                if strenght_set==False:
                    self.SetTopicValue(self.InterfaceTopicFormat(NIC_SIGNAL_STRENGHT_TOPIC,self.GetNicName(nic)), 0)


        # Traffic data
        self.SetTopicValue(DOWNLOAD_TRAFFIC_TOPIC, psutil.net_io_counters()[
                           1], self.ValueFormatter.TYPE_BYTE)
        self.SetTopicValue(UPLOAD_TRAFFIC_TOPIC, psutil.net_io_counters()[
                           0], self.ValueFormatter.TYPE_BYTE)



    # Signal strenght methods:
    def GetWirelessStrenght_Linux(self):
        p = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.read().decode()
        m = re.findall('(wl.*?) .*?Signal level=(-[0-9]+) dBm', out, re.DOTALL)
        p.communicate()
        return m

    def GetWirelessStrenght_Windows(self):
        p = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.read().decode(errors="ignore")
        if "Segnale" in out: # Italian support
            m = re.findall('Nome.*?:.*? ([A-z0-9 \-]*).*?Segnale.*?:.*?([0-9]*)%', out, re.DOTALL)
        elif "Signal" in out: # English support
            m = re.findall('Nome.*?:.*?([A-z0-9 ]*).*?Signal.*?:.*?([0-9]*)%', out, re.DOTALL)
        else:
            self.Log(self.Logger.LOG_ERROR,"Can't get signal strenght data in your region. Please open a Git issue with and show the output of this command in the CMD: 'netsh wlan show interfaces' ")
            self.supports_signal_strenght=False
            # TODO Remove the signal strenght topic for all the inets here !
        p.communicate()
        return m

    # OS entity information get

    def GetOS(self):
        # Get OS from OsSensor and get temperature based on the os
        os = self.FindEntity('Os')
        if os:
            if not os.postinitializeState: # I run this function in post initialize so the os sensor might not be ready
                os.CallPostInitialize()
            os.CallUpdate()
            return os.GetTopicValue()


    # Other entity settings

    # I have also contents with value (exclude_interfaces) in config
    def EntitySchema(self):
        schema = super().EntitySchema()
        schema = schema.extend({
            self.schemas.Optional(self.consts.CONTENTS_OPTION_KEY):  {
                self.schemas.Optional(EXCLUDE_INTERFACES_CONTENT_OPTION_KEY): self.schemas.Or(list, str),
                self.schemas.Optional(RENAME_INTERFACES_CONTENT_OPTION_KEY): dict
            }
        })
        return schema

    def InterfaceTopicFormat(self, topic,nic):
        return topic.format(nic)
        

    def ManageDiscoveryData(self, discovery_data):

        for nic in self.nics:
            for data in discovery_data:
                if self.GetNicName(nic) in data['name']: # Check if data of the correct nic
                    if NIC_ADDRESS_TOPIC.split("/")[-1] in data['name']: # Check if it's the private address
                        data['payload']['name'] = data['payload']['name'].split("-")[0] + "- " + NIC_PRIVATE_ADDRESS_DISCOVERY_NAME_FORMAT.format(self.GetNicName(nic))
                        data['payload']['icon'] = NIC_PRIVATE_ADDRESS_DISCOVERY_ICON
                    elif NIC_SIGNAL_STRENGHT_TOPIC.split("/")[-1] in data['name']: # Check if it's the signal strenght
                        data['payload']['name'] = data['payload']['name'].split("-")[0] + "- " + NIC_SIGNAL_STRENGHT_DISCOVERY_NAME_FORMAT.format(self.GetNicName(nic))
                        data['payload']['icon'] = NIC_SIGNAL_STRENGHT_DISCOVERY_ICON
                        data['payload']['unit_of_measurement'] = self.NIC_SIGNAL_STRENGHT_DISCOVERY_UNIT_OF_MEASUREMENT

        return discovery_data

    def GetNicName(self,nic,getRenamed=True):
        # On windows, the network interface name has only the id "{......}"
        name = nic
        try:
            if '{' in nic:
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                reg_key = winreg.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
                reg_subkey = winreg.OpenKey(reg_key, nic + r'\Connection')
                name = winreg.QueryValueEx(reg_subkey, 'Name')[0]
        except:
            name = nic

        if getRenamed:
            # In configuration, user can set a rename interfaces dict, with key=original name, value=new name
            rename_dict=self.GetOption([self.consts.CONTENTS_OPTION_KEY,RENAME_INTERFACES_CONTENT_OPTION_KEY],{})
            if name in rename_dict:
                return rename_dict[name]

        return name


    def RemoveSignalStrenghtTopics(self):
        # If not supported, I remove the signal strenght topic (also discovery won't include anymore this topic)
        for topic in self.outTopics:
            if topic['topic'].split("/")[-1] == NIC_SIGNAL_STRENGHT_TOPIC.split("/")[-1]:
                self.RemoveOutboundTopic(topic)

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