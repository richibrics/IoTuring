# IoTuring

Simple and powerful script to control your pc and share statistics using communication protocols like MQTT and home control hubs like HomeAssistant.

Like his predecessor - **PyMonitorMQTT** - IoTuring allows you to choose which data are sent and which command are expected to be given. 

**Why you should use this ?** You don't have to write your configurations manually, entities are updated asynchronously and multiple warehouses can be used with one single run (and this is not deprecated obviously!).

## Install

### Install Python

IoTuring needs Python3.7 or later to run.
You can install it [here](https://www.python.org/downloads/).

### Install PIP

To install required packages you need [pip](https://www.makeuseof.com/tag/install-pip-for-python/)

### Install dependencies

To install dependencies all together, you only have to type in your terminal a PIP command.
You need to install different packages depending on your operating system.

If you're running a Linux distro, run 

```
pip install -r requirements_linux.txt
```

If you're running Windows, run 

```
pip install -r requirements_win.txt
```

If you're running macOS, run 

```
pip install -r requirements_macos.txt
```

### Configure

The first time you run IoTuring you need to specify which entities and warehouses you want to enable.
To run in configuration mode, you only need to specify the '-c' argument along the script execution command:

```
python main.py -c
```

A simple menu will show and you will be able to configure your entities and warehouses !
Once you have selected your preferred settings, you're ready to run IoTuring.

You will be able to enter the configuration menu whenever you want (with the same command as above) to edit your choises.

### Run 

You can simply run IoTuring using this command

```
python main.py
```

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
- Power: permits remote poweroff, reboot and sleep commands
- Ram: shares useful information about ram usage
- Time: shares the machine local time
- Uptime: shares the time since the machine is on
- Username: shares the name of the user who is working on the machine

### Available warehouses

- HomeAssistant: shares sensors and switches to HomeAssistant. The machine is shown as a Device and all the entites are grouped together. **recommended**
- MQTT: sends data to MQTT broker and subscribes to commands topics.
- Console: prints data to the console
