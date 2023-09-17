from __future__ import annotations
import math
from IoTuring.Entity.ValueFormat import ValueFormatterOptions

# Value formatter
# If I have to return value not in byte but with MB/GB/KB; same for time

# OPTIONS MEANING (example with byte values)
# type: the type of the value (one of the ValueFormatter constants)
# size: True "means that will be used the nearest unit 1024Byte->1KB" False "send the value without using the pow1024 mechianism"
# size: MB "means that will be used the specified size 2014Byte->0.001MB"
# decimals: integer "the number of decimal for the value": -1 for untouched

# Lists of measure units
BYTE_SIZES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
TIME_SIZES = ['s', 'm', 'h', 'd']
FREQUENCY_SIZES = ['Hz', 'kHz', 'MHz', 'GHz']
TIME_SIZES_DIVIDERS = [1, 60, 60, 24]
CELSIUS_UNIT = '°C'

SPACE_BEFORE_UNIT = ' '

class ValueFormatter():
    
    # includeUnit: isn't in the option as it's chosen by each warehouse and not by the entity itself
    @staticmethod
    def FormatValue(value, options: ValueFormatterOptions | None, includeUnit: bool):
        """
        Format the value according to the options. Returns value as string.
        IncludeUnit: True if the unit has to be included in the value
        """
        return str(ValueFormatter._ParseValue(value, options, includeUnit))
    
    @staticmethod
    def _ParseValue(value, options: ValueFormatterOptions | None, includeUnit: bool):
        if options is None:
            return value
        valueType = options.get_value_type()
        
        # specific type formatting
        if valueType == ValueFormatterOptions.TYPE_NONE:  # edit needed only if decimals
            return ValueFormatter.roundValue(value, options)
        elif valueType == ValueFormatterOptions.TYPE_BYTE:
            return ValueFormatter.ByteFormatter(value, options, includeUnit)
        elif valueType == ValueFormatterOptions.TYPE_MILLISECONDS:
            return ValueFormatter.MillisecondsFormatter(value, options, includeUnit)
        elif valueType == ValueFormatterOptions.TYPE_TIME:
            return ValueFormatter.TimeFormatter(value, options, includeUnit)
        elif valueType == ValueFormatterOptions.TYPE_FREQUENCY:
            return ValueFormatter.FrequencyFormatter(value, options, includeUnit)
        elif valueType == ValueFormatterOptions.TYPE_TEMPERATURE:
            return ValueFormatter.TemperatureCelsiusFormatter(value, options, includeUnit)
        elif valueType == ValueFormatterOptions.TYPE_PERCENTAGE:
            if includeUnit:
                return str(value) + SPACE_BEFORE_UNIT + '%'
            else:
                return str(value)
        else:
            return str(value)

    @staticmethod
    def TimeFormatter(value, options: ValueFormatterOptions, includeUnit: bool):
        # Get value in seconds, and adjustable
        asked_size = options.get_adjust_size()

        if asked_size and asked_size in TIME_SIZES:
            index = TIME_SIZES.index(asked_size)
            divider = 1
            for i in range(0, index+1):
                divider = divider*TIME_SIZES_DIVIDERS[i]

            value = value/divider
        else:
            index = 0

        value = ValueFormatter.roundValue(value, options)
        result = str(value)

        if includeUnit:
            result = result + SPACE_BEFORE_UNIT + TIME_SIZES[index]

        return result

    @staticmethod
    def MillisecondsFormatter(value, options: ValueFormatterOptions, includeUnit: bool):
        # Get value in milliseconds: adjust not implemented
        
        value = ValueFormatter.roundValue(value, options)
        
        if includeUnit:
            return str(value) + SPACE_BEFORE_UNIT + 'ms'
        else:
            return str(value)

    # Get from number of bytes the correct byte size: 1045B is 1KB. If size_wanted passed and is SIZE_MEGABYTE, if I have 10^9B, I won't diplay 1GB but c.a. 1000MB
    @staticmethod
    def ByteFormatter(value, options: ValueFormatterOptions, includeUnit: bool):
        # Get value in bytes
        asked_size = options.get_adjust_size()
        decimals = options.get_decimals()

        if asked_size and asked_size in BYTE_SIZES:
            powOf1024 = BYTE_SIZES.index(asked_size)
        # If value == 0 math.log failes, so simply send 0:
        elif float(value) == 0:
            powOf1024 = 0
        else:
            powOf1024 = math.floor(math.log(value, 1024))

        value = value/(math.pow(1024, powOf1024))

        value = ValueFormatter.roundValue(value, options)

        result = str(value)

        if includeUnit:
            result = result + SPACE_BEFORE_UNIT + BYTE_SIZES[powOf1024]

        return result

    @staticmethod
    def FrequencyFormatter(value, options: ValueFormatterOptions, includeUnit: bool):
        # Get value in hertz, and adjustable
        asked_size = options.get_adjust_size()

        if asked_size and asked_size in FREQUENCY_SIZES:
            index = FREQUENCY_SIZES.index(asked_size)
            value = value/pow(1000,index)
        else:
            index = 0

        # decimals
        value = ValueFormatter.roundValue(value, options)

        result = str(value)
        
        if includeUnit:
            result = result + SPACE_BEFORE_UNIT + FREQUENCY_SIZES[index]
        return result


    @staticmethod
    def TemperatureCelsiusFormatter(value, options: ValueFormatterOptions, includeUnit: bool):
        # asked_size not implemented
        
        # decimals
        value = ValueFormatter.roundValue(value, options)

        result = str(value)
        
        if includeUnit:
            result = result + SPACE_BEFORE_UNIT + CELSIUS_UNIT 
        return result

    @staticmethod
    def roundValue(value, options: ValueFormatterOptions):
        if options.get_decimals() != ValueFormatterOptions.DO_NOT_TOUCH_DECIMALS:
            return round(value, options.get_decimals())
        return value