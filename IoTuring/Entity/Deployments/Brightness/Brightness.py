from IoTuring.Entity.Entity import Entity 
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.Entity.EntityData import EntitySensor, EntityCommand
from IoTuring.MyApp.SystemConsts.OperatingSystemDetection import OperatingSystemDetection as OsD
from IoTuring.Entity.ValueFormat import ValueFormatterOptions 
import subprocess
import re
import os
import sys


KEY = 'brightness'
KEY_STATE = 'brightness_state'

CONFIG_KEY_GPU = 'gpu'

VALUEFORMATTER_OPTIONS_PERCENT = ValueFormatterOptions(
    ValueFormatterOptions.TYPE_PERCENTAGE)

class Brightness(Entity):
    NAME = "Brightness"
    ALLOW_MULTI_INSTANCE = True


    def Initialize(self):        

        self.RegisterEntitySensor(
            EntitySensor(self, KEY_STATE,
                         supportsExtraAttributes=False,
                         valueFormatterOptions=VALUEFORMATTER_OPTIONS_PERCENT))
    
        
        
        if OsD.IsWindows():
            self.specificGetBrightness = self.GetBrightness_Win
            self.specificSetBrightness = self.SetBrightness_Win
            import wmi
            import pythoncom
        if OsD.IsMacos():
            self.specificGetBrightness = self.GetBrightness_macOS
            self.specificSetBrightness = self.SetBrightness_macOS
        if OsD.IsLinux():
            self.configuredGPU: str = self.GetFromConfigurations(CONFIG_KEY_GPU)
            self.specificGetBrightness = self.GetBrightness_Linux
            self.specificSetBrightness = self.SetBrightness_Linux
        else:
            self.Log(self.Logger.LOG_WARNING,
                     'No brightness sensor available for this operating system')
        
        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback, KEY_STATE))

    def Callback(self, message):
        state = message.payload.decode("utf-8")
        try:
            # Value from 0 and 100
            self.specificSetBrightness(int(state))
        except ValueError: # Not int -> not a message for that function
            return
        except Exception as e:
            raise Exception("Error during brightness set: " + str(e))
            

    def Update(self):
        brightness = self.specificGetBrightness()
        self.SetEntitySensorValue(KEY_STATE, brightness)

    def SetBrightness_macOS(self, value: str|int):
        value = value/100  # cause I need it from 0 to 1
        command = 'brightness ' + str(value)
        subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    def SetBrightness_Linux(self, value):
        # use acpi to controll backlight
        with open(f'/sys/class/backlight/{self.configuredGPU}/brightness', 'w') as file:
            file.write(f'{str(value)}\n')

    def SetBrightness_Win(self, value):
        pythoncom.CoInitialize()
        return wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(value, 0)

    def GetBrightness_macOS(self) -> float:
        try:
            command = 'brightness -l'
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            stdout = process.communicate()[0]
            brightness = re.findall(
                'display 0: brightness.*$', str(stdout))[0][22:30]
            brightness = float(brightness)*100  # is between 0 and 1
            return brightness
        except:
            raise Exception(
                'You sure you installed Brightness from Homebrew ? (else try checking you PATH)')

    def GetBrightness_Linux(self) -> int:
        # get the content of the file /sys/class/backlight/intel_backlight/brightness
        with open(f'/sys/class/backlight/{self.configuredGPU}/brightness', 'r') as file:
            content = file.read()
        brightness = int(content.strip('\n'))
        return self.ConvertBrightness(brightness, from_scale=255, to_scale=100)

    def GetBrightness_Win(self) -> int:
        return int(wmi.WMI(namespace='wmi').WmiMonitorBrightness()[0].CurrentBrightness)
    
    def ConvertBrightness(self, value, from_scale=255, to_scale=100) -> int:
        """Function to convert brightness values from one scale to another.
        
        Args:
            value (int): The brightness value to convert.
            from_scale (int): The original scale of the brightness value. Default is 255.
            to_scale (int): The target scale of the brightness value. Default is 100.
        
        Returns:
            float: The converted brightness value.
        """
        return int((value / from_scale) * to_scale)


    @classmethod    
    def ConfigurationPreset(cls):
        preset = MenuPreset()
        if OsD.IsLinux():
            # find all GPUs in /sys/class/backlight by listing all directories
            gpus = [gpu for gpu in os.listdir('/sys/class/backlight') if os.path.isdir(f'/sys/class/backlight/{gpu}')]

            preset.AddEntry(
                name="which GPUs backlight you want to control?",
                key=CONFIG_KEY_GPU,
                question_type='select',
                choices=gpus
                            )
        return preset
    
    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsWindows(): #TODO needs to be tested
            # if wmi and pythoncom are not available, raise an exception
            if ['wmi', 'pythoncom'] not in sys.modules:
                raise Exception(
                    'Brightness not available, have you installed \'wmi\' on pip ?')
        elif OsD.IsMacos(): #TODO needs to be tested
            if not OsD.CommandExists('brightness'):
                raise Exception(
                    'Brightness not avaidlable, have you installed \'brightness\' on Homebrew ?')
        elif OsD.IsLinux():
            if not os.path.exists('/sys/class/backlight'): #TODO check if this dir always exists
                raise Exception(
                    'Brightness not available, no backlight found in /sys/class/backlight')
        else:
            raise NotImplementedError('Brightness not available for this OS')