# IoTuring

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/ioturing.svg)](https://pypi.org/project/IoTuring/)
[![Build, release and publish](https://github.com/richibrics/IoTuring/actions/workflows/build-release-publish-with-vtag.yml/badge.svg)](https://github.com/richibrics/IoTuring/actions/workflows/build-release-publish-with-vtag.yml)

Simple and powerful cross-platform script to control your pc and share statistics using communication protocols like MQTT and home control hubs like **HomeAssistant**.

Like his predecessor - **PyMonitorMQTT** - IoTuring allows you to choose which data are sent and which command are expected to be given. 

**Why should you use this ?** You don't have to write your configurations manually, entities are updated asynchronously and multiple warehouses can be used with one single run (and this is not deprecated obviously!). 

But the most important thing: **works on all OSs and all architectures ! Windows, Linux, macOS, openBSD; x86, amd64, ARM and so on...**

## Install

You can easily install IoTuring through pip. Although the version is os-specific, so follow the instructions below to install the right version for your operating system.

### Requirements

- [Git](https://git-scm.com/)
- [Python 3.7+](https://www.python.org/downloads/)
- [Pip](https://www.makeuseof.com/tag/install-pip-for-python/)

Some platforms may need other software for some entities.

#### Install all requirements on ArchLinux

```shell
pacman -Syu base-devel git python python-pip
```

#### Install and update all requirements on Debain

```shell
apt install git python3 python3-pip libdbus-glib-1-dev
pip install --upgrade pip
```

#### Install and update all requirements on Ubuntu

```
apt install git python3 python3-pip libdbus-glib-1-dev meson patchelf
pip install --upgrade pip
```

#### Windows

- [Python](https://www.python.org/downloads/), pip included
- [Git](https://git-scm.com/download/win), just accept the defaults

### Download and install with pip

On Linux:

```shell
pip install IoTuring[linux]
```

On Windows:

```shell
py -m pip install IoTuring[win]
```

Note: on Windows you have to prefix every command with `py -m` as here.

On MacOs:

```shell
pip install IoTuring[macos]
```

### Configure

The first time you run IoTuring you need to specify which entities and warehouses you want to enable.
To run in configuration mode, you only need to specify the '-c' argument along the script execution command:

```
IoTuring -c
```

A simple menu will show and you will be able to configure your entities and warehouses !
Once you have selected your preferred settings, you're ready to run IoTuring.

You will be able to enter the configuration menu whenever you want (with the same command as above) to edit your choises.

### Run 

You can simply run IoTuring using this command

```
IoTuring
```

### HomeAssistant demo

Your computer will show up in HomeAssistant as a single Device, so all your entities will be grouped together. 
The device will also have some properties like connectivity and battery status.

You can see how your device will appear under the Devices section in Home Assistant in the following GIF (wait until it's loaded):


![device](https://user-images.githubusercontent.com/12238652/187725698-dafceb9c-c746-4a84-9b2c-caf5ea46a802.gif)

All sensors and switches will be available to be added to your dashboard in your favourite cards !

### Available entities

- ActiveWindow: shares the name of the window you're working on
- AppInfo: shares app informations like the running version
- Battery: shares the battery level and charging status
- BootTime: shares the machine boot time
- Cpu: shares useful information about cpu usage (times, frequencies, percentages) 
- DesktopEnvironment: shares the running desktop environment (useful only for Linux)
- Disk: shares disk usage data
- Hostname: shares the machine hostname
- Lock: permits a remote lock command to lock the machine
- Monitor: permits remote monitors control commands
- Notify: permits remote notify show on your machine
- Os: shares the operating system of your machine
- Power*: permits remote poweroff, reboot and sleep commands
- Ram: shares useful information about ram usage
- Time: shares the machine local time
- Uptime: shares the time since the machine is on
- Username: shares the name of the user who is working on the machine

\* To use the features from Power entity on Linux and macOS you need to give permissions to your user to shutdown and reboot without sudo password.
You can easily do that by adding the following line at the end of the "/etc/sudoers" file (you can use the following command: sudo nano /etc/sudoers):

```
YOURUSERNAMEHERE ALL=(ALL) NOPASSWD: /sbin/poweroff, /sbin/reboot, /sbin/shutdown
```

Change **YOURUSERNAMEHERE** with the user that runs the script.

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

### Versioning

The project uses [calendar versioning](https://calver.org/):

`YYYY.0M.n`:

- `YYYY`: Full year: 2022, 2023 ...
- `0M`: Zero-padded month: 01, 02 ... 11, 12
- `n`: Build number in the month: 1, 2 ...
