LOGS_FOLDER = "Logs"
DEFAULT_LOG_LEVEL = "INFO"
MIN_CONSOLE_WIDTH = 95

LOG_PREFIX_PARTS = [
    {
        "attr": "asctime",
        "len": 19
    },
    {
        "attr": "levelname:^8s",
        "len": 8
    },
    {
        "attr": "source:^30s",
        "len": 30
    }
]

LOG_PREFIX_FORMAT = "[ {} | {} | {} ] "
LOG_PREFIX_STRING = LOG_PREFIX_FORMAT.format(
    *["{" + f["attr"] + "}" for f in LOG_PREFIX_PARTS])


# On/off states as strings:
STATE_ON = "ON"
STATE_OFF = "OFF"
