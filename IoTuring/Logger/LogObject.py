from IoTuring.Logger.Logger import Logger

class LogObject:
    from IoTuring.Logger.consts import LOG_INFO, LOG_MESSAGE, LOG_ERROR, LOG_DEBUG, LOG_DEVELOPMENT, LOG_WARNING

    def Log(self, messageType, message):
        Logger.getInstance().Log(
            source=self.LogSource(),
            message=message,
            messageType=messageType
        )

    # to override in classes where I want a source different from class name
    def LogSource(self):
        return type(self).__name__
   