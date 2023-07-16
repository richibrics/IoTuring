from IoTuring.Logger import consts
from IoTuring.Logger.Colors import Colors


class LogLevel:
    """ A loglevel with numeric and string values"""

    def __init__(self, level_const: str) -> None:
        level_dict = next(
            (l for l in consts.LOG_LEVELS if l["const"] == level_const), None)

        if not level_dict:
            raise Exception(f"Unknown log level: {level_const}")

        self.const = level_const
        self.string = level_dict["string"]
        self.number = int(level_dict["number"])
        if "color" in level_dict.keys():
            self.color = getattr(Colors, level_dict["color"])
        else:
            self.color = None

    def __str__(self) -> str:
        return self.string

    def __int__(self) -> int:
        return self.number

    def get_colored_string(self, string: str) -> str:
        """ Get colored text according to LogLevel """
        if self.color:
            out_string = self.color + string + Colors.reset
        else:
            out_string = string
        return out_string



class LogLevelObject:
    """ Base class for loglevel properties """

    LOG_MESSAGE = LogLevel("LOG_MESSAGE")
    LOG_ERROR = LogLevel("LOG_ERROR")
    LOG_WARNING = LogLevel("LOG_WARNING")
    LOG_INFO = LogLevel("LOG_INFO")
    LOG_DEBUG = LogLevel("LOG_DEBUG")
    LOG_DEVELOPMENT = LogLevel("LOG_DEVELOPMENT")
