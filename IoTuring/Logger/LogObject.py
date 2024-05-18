from IoTuring.Logger.Logger import Logger
from IoTuring.Logger.LogLevel import LogLevelObject, LogLevel

class LogObject(LogLevelObject):

    def Log(self, loglevel: LogLevel, message, **kwargs):
        logger = Logger()
        logger.Log(
            source=self.LogSource(),
            message=message,
            loglevel=loglevel,
            **kwargs
        )

    # to override in classes where I want a source different from class name
    def LogSource(self):
        return type(self).__name__
