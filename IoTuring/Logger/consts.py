LOGS_FOLDER = "Logs"
LOG_FILENAME_FORMAT = "Log_%Y-%m-%d_%H:%M:%S.log"
MESSAGE_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


LOG_MESSAGE = 0
LOG_ERROR = 1
LOG_WARNING = 2
LOG_INFO = 3
LOG_DEBUG = 4
LOG_DEVELOPMENT = 5


# On/off states as strings:
STATE_ON = "ON"
STATE_OFF = "OFF"

# Fill start of string with spaces to jusitfy the message (0: no padding)
# First for type, second for source
STRINGS_LENGTH = [8, 30]

# number of spaces to separe the message from the previuos part of the row
PRESTRING_MESSAGE_SEPARATOR_LEN = 2
# before those spaces I add this string
LONG_MESSAGE_PRESTRING_CHAR = ' '

CONSOLE_LOG_LEVEL = LOG_INFO
FILE_LOG_LEVEL = LOG_WARNING

MESSAGE_WIDTH = 95
