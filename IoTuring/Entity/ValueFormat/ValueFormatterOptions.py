class ValueFormatterOptions():  
    TYPE_NONE = 0
    TYPE_BYTE = 1
    TYPE_TIME = 2
    TYPE_PERCENTAGE = 3
    TYPE_FREQUENCY = 4
    TYPE_MILLISECONDS = 5
    TYPE_TEMPERATURE = 6

    DO_NOT_TOUCH_DECIMALS = -1
      
    def __init__(self, value_type=TYPE_NONE, decimals=DO_NOT_TOUCH_DECIMALS, adjust_size=None):
        self.value_type = value_type
        self.decimals = decimals
        self.adjust_size = adjust_size
        
    def set_value_type(self, value_type):
        self.value_type = value_type
        
    def set_decimals(self, decimals):
        self.decimals = decimals
        
    def set_adjust_size(self, adjust_size):
        self.adjust_size = adjust_size
        
    def get_value_type(self):
        return self.value_type
    
    def get_decimals(self):
        return self.decimals

    def get_adjust_size(self):
        return self.adjust_size
    