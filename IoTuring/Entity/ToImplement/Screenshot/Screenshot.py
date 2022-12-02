import os
import pyscreenshot as ImageGrab
from PIL import Image
from IoTuring.Entity.Entity import Entity 


TOPIC = 'screenshot'

SCREENSHOT_FILENAME = 'screenshot.png'
scriptFolder = str(os.path.dirname(os.path.realpath(__file__)))


class Screenshot(Entity):
    def Initialize(self):
        self.AddTopic(TOPIC)

    def Update(self):
        self.SetTopicValue(TOPIC, self.TakeScreenshot())

    def TakeScreenshot(self):
        filename = os.path.join(scriptFolder, SCREENSHOT_FILENAME)
        ImageGrab.grab().save(filename)
        f = open(filename, "rb")  # 3.7kiB in same folder
        fileContent = f.read()
        image = bytearray(fileContent)
        f.close()
        os.remove(filename)
        return image

    def ManageDiscoveryData(self, discovery_data):
        # Camera must not have some information that sensors have so here they have to be removed ! (done with expire_after)
         
        discovery_data[0]['payload'].pop('state_topic', None)
        discovery_data[0]['payload']['topic']=self.SelectTopic({"topic":TOPIC})

        if 'expire_after' in discovery_data[0]['payload']: # Camera must not have this information or will be discarded
            del(discovery_data[0]['payload']['expire_after'])
        
        '''
        discovery_data[0]['payload']['availability']={}
        discovery_data[0]['payload']['availability']['topic']=self.SelectTopic("status")
        discovery_data[0]['payload']['availability']['payload_available']=ONLINE_STATE
        discovery_data[0]['payload']['availability']['payload_not_available']=OFFLINE_STATE
        '''
        return discovery_data