from IoTuring.Configurator import ConfiguratorIO


HELP_MESSAGE = f"""
1. Configuration file

\tYou can find the configuration file in the following path: 
\t\tmacOS\t\t~/Library/Application Support/IoTuring/configurations.json 
\t\tLinux\t\t~/.config/IoTuring/configurations.json 
\t\tWindows\t\t%APPDATA%/IoTuring/configurations.json
\t\tFallback\t[ioturing_install_path]/Configurator/configurations.json\t
\tYou can also set your preferred directory by setting the environment variable {ConfiguratorIO.CONFIG_PATH_ENV_VAR} 
\tConfiguration will be stored there in the file configurations.json.

2.Configurator menu

\tUse Escape to go back to the previous menu
\tUse ctrl+C to exit without saving
"""

PRESET_RULES = """Options with this sign are compulsory: {!}
Use Escape to cancel"""