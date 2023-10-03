# IoTuring

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/ioturing.svg)](https://pypi.org/project/IoTuring/)
[![Build, release and publish](https://github.com/richibrics/IoTuring/actions/workflows/build-release-publish-with-vtag.yml/badge.svg)](https://github.com/richibrics/IoTuring/actions/workflows/build-release-publish-with-vtag.yml)

If you really like this project and you would like to support it:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/richibrics)

# The project

Simple and powerful cross-platform script to control your pc and share statistics using communication protocols like MQTT and home control hubs like **HomeAssistant**.

Like his predecessor - **PyMonitorMQTT** - IoTuring allows you to choose which data are sent and which command are expected to be given. 

**Why should you use this ?** You don't have to write your configurations manually, entities are updated asynchronously and multiple warehouses can be used with one single run (and this is not deprecated obviously!). 

But the most important thing: **works on all OSs and all architectures ! Windows, Linux, macOS, openBSD; x86, amd64, ARM and so on...**

**CHANGELOG**: available in [Releases](https://github.com/richibrics/IoTuring/releases) page

## Install

### Who knows how it works

Using pip (on Python >= 3.7) install the IoTuring package

```shell
pip install IoTuring
```

Run with `IoTuring` or `python -m IoTuring`

Configure with `IoTuring -c` or `python -m IoTuring -c`

### Who doesn't know how it works

#### Requirements

- [Python 3.7+](https://www.python.org/downloads/)
- [Pip](https://www.makeuseof.com/tag/install-pip-for-python/)

Some platforms may need other software for some entities.

##### Install all requirements on ArchLinux

```shell
pacman -Syu python python-pip
```

##### Install and update all requirements on Debian or Ubuntu

```shell
apt install python3 python3-pip -y
pip install --upgrade pip
```

##### Windows

- [Python](https://www.python.org/downloads/), pip included

#### Download and install with pip

On Linux and macOS:

```shell
pip install IoTuring
```

On Windows:

```shell
py -m pip install IoTuring
```

Note: on Windows you have to prefix every command with `py -m` as here.

#### Configure

The first time you run IoTuring you need to specify which entities and warehouses you want to enable.
To run in configuration mode, you only need to specify the '-c' argument along the script execution command:

```
python -m IoTuring -c
```

A simple menu will show and you will be able to configure your entities and warehouses !
Once you have selected your preferred settings, you're ready to run IoTuring.

You will be able to enter the configuration menu whenever you want (with the same command as above) to edit your choises.

#### Run 

You can simply run IoTuring using this command

```
IoTuring
```

or this one

```
python -m IoTuring
```

## Docker

Run the configurator:

```shell
docker run -it -v ./.config/IoTuring/:/config ghcr.io/richibrics/ioturing:latest IoTuring -c
```

Enable the `Console Warehouse` to see logs!

Run detached after configuration:

```shell
docker run -d -v ./.config/IoTuring/:/config ghcr.io/richibrics/ioturing:latest
```

For a docker compose example see [docker-compose.yaml](./docker-compose.yaml). Create configuration manually or with the command above!

## HomeAssistant demo

Your computer will show up in HomeAssistant as a single Device, so all your entities will be grouped together. 
The device will also have some properties like connectivity and battery status.

You can see how your device will appear under the Devices section in Home Assistant in the following GIF (wait until it's loaded):


![device](https://github.com/richibrics/IoTuring/blob/main/docs/images/homeassistant-demo.gif?raw=true)

All sensors and switches will be available to be added to your dashboard in your favourite cards !

## Features

### Available entities

| Name               | Description                                                                 | Supported platforms                                                                     |
| ------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| ActiveWindow       | shares the name of the window you're working on                             | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| AppInfo            | shares app informations like the running version                            | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Battery            | shares the battery level and charging status                                | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| BootTime           | shares the machine boot time                                                | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Cpu                | shares useful information about cpu usage (times, frequencies, percentages) | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| DesktopEnvironment | shares the running desktop environment (useful only for Linux)              | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Disk               | shares disk usage data                                                      | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| DisplayMode        | command for changing multimonitor display mode                              | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) |
| Hostname           | shares the machine hostname                                                 | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Lock               | command for locking the machine                                             | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Monitor            | command for switching monitors on/off                                       | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                             |
| Notify             | displays a notification                                                     | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| OperatingSystem    | shares the operating system of your machine                                 | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Power*             | commands for poweroff, reboot and sleep                                     | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Ram                | shares useful information about ram usage                                   | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Time               | shares the machine local time                                               | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Temperature        | shares temperature sensor data                                              | ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                             |
| Terminal           | runs custom commands in the shell                                           | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Uptime             | shares the time since the machine is on                                     | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Username           | shares the name of the user who is working on the machine                   | ![win](https://github.com/richibrics/IoTuring/blob/main/docs/images/win.png?raw=true) ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png) |
| Volume             | control audio volume                                                        | ![mac](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/mac.png) ![linux](https://raw.githubusercontent.com/richibrics/IoTuring/main/docs/images/linux.png)                                                             |


\* To use the features from Power entity on Linux and macOS you need to give permissions to your user to shutdown and reboot without sudo password.
You can easily do that by using the following terminal command:

```shell
sudo sh -c "echo '$USER ALL=(ALL) NOPASSWD: /sbin/poweroff, /sbin/reboot, /sbin/shutdown' >> /etc/sudoers"
```


### Available warehouses

- HomeAssistant: shares sensors and switches to HomeAssistant. The machine is shown as a Device and all the entites are grouped together. **recommended**
- MQTT: sends data to MQTT broker and subscribes to commands topics.
- Console: prints data to the console


## Development

### Editable install

[Pip documentation](https://pip.pypa.io/en/stable/topics/local-project-installs/)

```shell
git clone https://github.com/richibrics/IoTuring
cd IoTuring
pip install -e .
```

Then run it like in the non-editable mode.

Warning: sometimes to run the module in editable mode you need to cd into the upper IoTuring folder.

### Debug log

Overwrite log level with the `IOTURING_LOG_LEVEL` environment variable. For example to run IoTuring with debug log:

```shell
env IOTURING_LOG_LEVEL=LOG_DEBUG IoTuring
```

### Versioning

The project uses [calendar versioning](https://calver.org/):

`YYYY.M.n`:

- `YYYY`: Full year: 2022, 2023 ...
- `M`: Month: 1, 2 ... 11, 12
- `n`: Build number in the month: 1, 2 ...

### Tests

To run tests in docker:

```shell
docker run --rm -it -v .:/srv/IoTuring:ro python:3.8.17-slim-bullseye /srv/IoTuring/tests/run_tests.sh
```

### Docker

To build docker image:

```
docker build -t ioturing:latest .
```

## Contributors

- [@richibrics](https://github.com/richibrics): Riccardo Briccola - Author
- [@infeeeee](https://github.com/infeeeee) - Main contributor
- [@tsunglung](https://github.com/tsunglung)

## Acknowledgement

Icons in this readme are from [Material Design Icons](https://materialdesignicons.com/), License: [Pictogrammers Free License](https://github.com/Templarian/MaterialDesign-SVG/blob/master/LICENSE)

Notification icon is from [Home Assistant](https://github.com/home-assistant/assets/): License: [CC BY-SA 4.0](https://github.com/home-assistant/assets/blob/master/LICENSE.md)
