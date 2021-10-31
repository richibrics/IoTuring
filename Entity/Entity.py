from Logger.Logger import Logger

class Entity:

    def __init__(self) -> None:
        self.initializeState=False
        self.postinitializeState=False
        self.name = "Unnamed"


    def Initialize(self):  # Implemented in sub-classes
        pass

    def CallInitialize(self): 
        try:
            self.Initialize()
            self.initializeState=True
            self.Log(Logger.LOG_INFO,"Initialization successfully completed")
        except Exception as e:
            self.Log(Logger.LOG_ERROR,"Initialization interrupted due to an error")
            self.Log(Logger.LOG_ERROR,e)
            del(self)
    

    def PostInitialize(self):  # Implemented in sub-classes
        pass

    def CallPostInitialize(self):  
        try:
            self.PostInitialize()
            self.postinitializeState=True
            self.Log(Logger.LOG_INFO,"Post-initialization successfully completed")
        except Exception as e:
            self.Log(Logger.LOG_ERROR,"Post-initialization interrupted due to an error")
            self.Log(Logger.LOG_ERROR,e)
            del(self)

    def Log(self, messageType, message):
        Logger.getInstance().Log(messageType, self.name + " Entity", message)

        