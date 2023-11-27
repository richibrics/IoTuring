from IoTuring.Configurator import ConfiguratorIO


HELP_MESSAGE = f"""
You can find the configuration file in the following path: 
\tmacOS\t\t~/Library/Application Support/IoTuring/configurations.json 
\tLinux\t\t~/.config/IoTuring/configurations.json 
\tWindows\t\t%APPDATA%/IoTuring/configurations.json
\tFallback\t[ioturing_install_path]/Configurator/configurations.json

You can also set your preferred directory by setting the environment variable {ConfiguratorIO.CONFIG_PATH_ENV_VAR} 
Configuration will be stored there in the file configurations.json.
"""

PRESET_RULES = "Options with this sign are compulsory: {!}"