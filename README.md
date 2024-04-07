# IoTuring

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/ioturing.svg)](https://pypi.org/project/IoTuring/)
[![Build, release and publish](https://github.com/richibrics/IoTuring/actions/workflows/build-release-publish-with-vtag.yml/badge.svg)](https://github.com/richibrics/IoTuring/actions/workflows/build-release-publish-with-vtag.yml)

If you really like this project and you would like to support it:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/richibrics)

## The project

Simple and powerful cross-platform script to control your pc and share statistics using communication protocols like MQTT and home control hubs like **HomeAssistant**.

Like his predecessor - **PyMonitorMQTT** - IoTuring allows you to choose which data are sent and which command are expected to be given. 

**Why should you use this ?** You don't have to write your configurations manually, entities are updated asynchronously and multiple warehouses can be used with one single run (and this is not deprecated obviously!). 

But the most important thing: **works on all OSs and all architectures ! Windows, Linux, macOS, openBSD; x86, amd64, ARM and so on...**

**CHANGELOG**: available in [Releases](https://github.com/richibrics/IoTuring/releases) page

### HomeAssistant preview

When the HomeAssistant warehouse is active, your computer will automatically show up in HomeAssistant as a single device, so all your entities will be grouped together. 
The device will also have some properties like connectivity and battery status.

![device](https://github.com/richibrics/IoTuring/blob/main/docs/images/device_info.png?raw=true)

All sensors and switches will be ready to be added to your dashboard in your favourite cards !

For detailed instructions about how to add your computer to HomeAssistant, look at the [HomeAssistant setup](#homeassistant-setup) section below.

## Install

### With pipx (recommended)

1. Install [pipx](https://pipx.pypa.io/), follow documentation according to your OS
2. Install IoTuring with pipx:
```shell
pipx install IoTuring
```
3. Done! You can configure IoTuring now.

### Detailed instructions

<details>
<summary>Debian/Ubuntu with pipx</summary>

```shell
sudo apt update
sudo apt install pipx
pipx ensurepath
pipx install IoTuring
```

</details>

<details>
<summary>ArchLinux with pipx</summary>

```
pacman -Syu python-pipx
pipx ensurepath
pipx install IoTuring
```
</details>

<details>
<summary>Windows with pipx</summary>

1. Download latest python https://www.python.org/downloads/
2. Install with default options
3. In a CommandPrompt or in Powershell window:
```shell
py -m pip install --user pipx
py -m pipx ensurepath
py -m pipx install IoTuring
```

4. Close and reopen the window, and you can run `IoTuring` without any prefixes.
</details>

<details>
<summary>Manual install from git to a virtual environment</summary>

Requirements:
- Python 3.8+
- Pip
- Git

```shell
git clone https://github.com/richibrics/IoTuring
cd IoTuring
mkdir .venv
python -m venv .venv
. ./.venv/bin/activate
pip install --upgrade pip
pip install .
```
</details>

<details>
<summary>With system pip (not recommended)</summary>

Requirements:
- Python 3.8+
- Pip

```shell
pip install IoTuring
```

</details>

## Configure

The first time you run IoTuring you need to specify which entities and warehouses you want to enable.
To run in configuration mode, you only need to specify the `-c` argument along the script execution command:

```
IoTuring -c
```

A simple menu will show and you will be able to configure your entities and warehouses !
Once you have selected your preferred settings, you're ready to run IoTuring.

You will be able to enter the configuration menu whenever you want (with the same command as above) to edit your choises.

## Run 

You can simply run IoTuring using this command:

```
IoTuring
```

### Other arguments

To see all command options run `IoTuring --help`:

```
> IoTuring --help
usage: IoTuring [-h] [-v] [-c] [-o]

Simple and powerful cross-platform script to control your pc and share statistics using communication protocols like MQTT and home control hubs like HomeAssistant.

options:
  -h, --help          show this help message and exit
  -v, --version       show program's version number and exit
  -c, --configurator  enter configuration mode
  -o, --open-config   open config file

Start without argument for normal use
```

## Docker

Run the configurator:

```shell
docker run -it -v ./.config/IoTuring/:/config richibrics/ioturing:latest IoTuring -c
```

Enable the `Console Warehouse` to see logs!

Run detached after configuration:

```shell
docker run -d -v ./.config/IoTuring/:/config richibrics/ioturing:latest
```

For a docker compose example see [docker-compose.yaml](./docker-compose.yaml). Create configuration manually or with the command above!


### HomeAssistant setup

Steps to connect IoTuring to your HomeAssistant install:

1. Install an MQTT broker. You can find the full list of brokers here: https://mqtt.org/software/
    - If you have a HAOS or supervised installation you can use the [Mosquitto broker addon](https://mqtt.org/software/)
    - For Docker users the official [eclipse-mosquitto container](https://hub.docker.com/_/eclipse-mosquitto/) is recommended
2.  Enable the [MQTT integration](https://www.home-assistant.io/integrations/mqtt) in HA, and connect to your broker
3.  Install and configure IoTuring, in the configurator menu add the HomeAssistant Warehouse, connect to the same broker
4.  When you start IoTuring, your computer will show up as a new MQTT device in HA automagically


## Features

### Available entities

| Name               | Description                                                                 | Supported platforms                                                                                                                                                                                                                                                     |
| ------------------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ActiveWindow       | shares the name of the window you're working on                             | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| AppInfo            | shares app informations like the running version                            | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Battery            | shares the battery level and charging status                                | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| BootTime           | shares the machine boot time                                                | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Cpu                | shares useful information about cpu usage (times, frequencies, percentages) | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| DesktopEnvironment | shares the running desktop environment (useful only for Linux)              | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Disk               | shares disk usage data                                                      | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| DisplayMode        | command for changing multimonitor display mode                              | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true)                                                                                                                                                                                   |
| Fanspeed           | shares maximum fanspeed of each controller                                  | ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                                                                                                                                                                              |
| Hostname           | shares the machine hostname                                                 | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Lock               | command for locking the machine                                             | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Monitor            | command for switching monitors on/off                                       | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                                                                                        |
| Notify             | displays a notification                                                     | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| OperatingSystem    | shares the operating system of your machine                                 | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Power*             | commands for poweroff, reboot and sleep                                     | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Ram                | shares useful information about ram usage                                   | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Temperature        | shares temperature sensor data                                              | ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                                                                                       |
| Terminal           | runs custom commands in the shell                                           | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Time               | shares the machine local time                                               | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Uptime             | shares the time since the machine is on                                     | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Username           | shares the name of the user who is working on the machine                   | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Volume             | control audio volume                                                        | ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                                                                                       |


\* To use the features from Power entity on macOS and on some Linux distros you need to give permissions to your user to shutdown and reboot without sudo password.
You can easily do that by using the following terminal command:

```shell
sudo sh -c "echo '$USER ALL=(ALL) NOPASSWD: /sbin/poweroff, /sbin/reboot, /sbin/shutdown' >> /etc/sudoers"
```


### Available warehouses

- HomeAssistant: shares sensors and switches to HomeAssistant. The machine is shown as a Device and all the entites are grouped together. **recommended**
- MQTT: sends data to MQTT broker and subscribes to commands topics.
- Console: prints data to the console


## Environment variables

- `IOTURING_CONFIG_DIR`: Change the path to the directory of the config file
- `IOTURING_LOG_LEVEL`: Set the log level

To run IoTuring with debug log on Linux or  on Mac run:

```shell
env IOTURING_LOG_LEVEL=LOG_DEBUG IoTuring
```

On Windows:

```cmd
set "IOTURING_LOG_LEVEL=LOG_DEBUG" && IoTuring
```

## Development

See [DEVELOPMENT.md](docs/DEVELOPMENT.md)

## Contributors

- [@richibrics](https://github.com/richibrics): Riccardo Briccola - Author
- [@infeeeee](https://github.com/infeeeee) - Main contributor
- [@tsunglung](https://github.com/tsunglung)

## Acknowledgement

Icons in this readme are from [Material Design Icons](https://materialdesignicons.com/), License: [Pictogrammers Free License](https://github.com/Templarian/MaterialDesign-SVG/blob/master/LICENSE)

Notification icon is from [Home Assistant](https://github.com/home-assistant/assets/): License: [CC BY-SA 4.0](https://github.com/home-assistant/assets/blob/master/LICENSE.md)
