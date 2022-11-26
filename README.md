# IoTuring

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Simple and powerful cross-platform script to control your pc and share statistics using communication protocols like MQTT and home control hubs like **HomeAssistant**.

Like his predecessor - **PyMonitorMQTT** - IoTuring allows you to choose which data are sent and which command are expected to be given. 

**Why should you use this ?** You don't have to write your configurations manually, entities are updated asynchronously and multiple warehouses can be used with one single run (and this is not deprecated obviously!). 

But the most important thing: **works on all OSs and all architectures ! Windows, Linux, macOS, openBSD; x86, amd64, ARM and so on...**

## Install

### Install Python

IoTuring needs Python3.7 or later to run.
You can install it [here](https://www.python.org/downloads/).

### Install PIP

To install required packages you need [pip](https://www.makeuseof.com/tag/install-pip-for-python/)

### Install dependencies

To install dependencies all together, you only have to type in your terminal a PIP command.
You need to install different packages depending on your operating system.

On Linux:

```shell
pip install .[linux]
```

On Windows:

```shell
pip install .[win]
```

On MacOs:

```shell
pip install .[macos]
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

Your computer will show in HomeAssistant as a single Device, so all your entities will be grouped together. 
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
