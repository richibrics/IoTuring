import math

# Value formatter
# If I have to return value not in byte but with MB/GB/KB; same for time

# OPTIONS MEANING (example with byte values)
# type: the type of the value (one of the ValueFormatter constants)
# size: True "means that will be used the nearest unit 1024Byte->1KB" False "send the value without using the pow1024 mechianism"
# size: MB "means that will be used the specified size 2014Byte->0.001MB"
# decimals: integer "the number of decimal for the value": -1 for untouched

ENABLE_UNIT = False

VALUEFORMATTER_OPTIONS_TYPE_KEY = "type"
VALUEFORMATTER_OPTIONS_DECIMALS_KEY = "decimals"
VALUEFORMATTER_OPTIONS_SIZE_KEY = "size"

# Lists of measure units
BYTE_SIZES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
TIME_SIZES = ['s', 'm', 'h', 'd']
TIME_SIZES_DIVIDERS = [1,60,60,24]

DO_NOT_TOUCH_DECIMALS = -1

class ValueFormatter():
    TYPE_NONE = 0
    TYPE_BYTE = 1
    TYPE_TIME = 2
    TYPE_PERCENTAGE = 3
    TYPE_FREQUENCY = 4
    TYPE_MILLISECONDS = 5

    @staticmethod
    def GetFormattedValue(value, options):
        valueType = options[VALUEFORMATTER_OPTIONS_TYPE_KEY]
        if valueType == ValueFormatter.TYPE_NONE:  # edit needed only if decimals 
            if options[VALUEFORMATTER_OPTIONS_DECIMALS_KEY] == DO_NOT_TOUCH_DECIMALS:
                return value
            else:
                return round(value, options[VALUEFORMATTER_OPTIONS_DECIMALS_KEY])
        elif valueType == ValueFormatter.TYPE_BYTE:
            return ValueFormatter.ByteFormatter(value,options)
        elif valueType == ValueFormatter.TYPE_MILLISECONDS:
            return ValueFormatter.MillisecondsFormatter(value, options)
        elif valueType == ValueFormatter.TYPE_TIME:
            return ValueFormatter.TimeFormatter(value, options)
        elif valueType == ValueFormatter.TYPE_FREQUENCY:
            return ValueFormatter.FrequencyFormatter(value, options)
        elif valueType == ValueFormatter.TYPE_PERCENTAGE:
            if ENABLE_UNIT:
                return str(value) + '%'
            else:
                return str(value)
        else:
            return str(value)
 
    @staticmethod
    def TimeFormatter(value,options):
        # Get value in seconds, and adjustable
        asked_size = options[VALUEFORMATTER_OPTIONS_SIZE_KEY]
        decimals = options[VALUEFORMATTER_OPTIONS_DECIMALS_KEY]
        
        if asked_size and asked_size in TIME_SIZES:
            index = TIME_SIZES.index(asked_size)
            divider = 1
            for i in range(0, index+1):
                divider = divider*TIME_SIZES_DIVIDERS[i]

            if decimals != DO_NOT_TOUCH_DECIMALS:
                result = str(round(value/divider, decimals))
            else:
                result = str(value/divider)
        else:
            result = str(result)
            index = 0

        if ENABLE_UNIT:
            result = result + TIME_SIZES[index]
    
        return result

    @staticmethod
    def MillisecondsFormatter(value, options):
        # Get value in milliseconds: adjust not implemented
        if ENABLE_UNIT:
            return str(value) + 'ms'
        else:
            return str(value)

    # Get from number of bytes the correct byte size: 1045B is 1KB. If size_wanted passed and is SIZE_MEGABYTE, if I have 10^9B, I won't diplay 1GB but c.a. 1000MB   
    @staticmethod
    def ByteFormatter(value, options):
        # Get value in bytes
        asked_size = options[VALUEFORMATTER_OPTIONS_SIZE_KEY]
        decimals = options[VALUEFORMATTER_OPTIONS_DECIMALS_KEY]
        
        if asked_size and asked_size in BYTE_SIZES:
            powOf1024 = BYTE_SIZES.index(asked_size)
        # If value == 0 math.log failes, so simply send 0:
        elif float(value) == 0:
            powOf1024 = 0
        else:
            powOf1024 = math.floor(math.log(value, 1024))

        if decimals != DO_NOT_TOUCH_DECIMALS:
            result = str(round(value/(math.pow(1024, powOf1024)), decimals))
        else:
            result = str(value/(math.pow(1024, powOf1024)))

        if ENABLE_UNIT:
            result = result + BYTE_SIZES[powOf1024]
    
        return result


    @staticmethod
    def FrequencyFormatter(value, options):
        # Get value in hertz
        if ENABLE_UNIT:
            return str(value) + 'Hz'
        else:
            return str(value)

    @staticmethod
    def Options(value_type = TYPE_NONE, decimals=DO_NOT_TOUCH_DECIMALS, adjust_size=None):
        return {VALUEFORMATTER_OPTIONS_TYPE_KEY: value_type, VALUEFORMATTER_OPTIONS_DECIMALS_KEY: decimals, VALUEFORMATTER_OPTIONS_SIZE_KEY:adjust_size}
