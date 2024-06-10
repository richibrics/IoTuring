# Autostart tips

Built-in autostart functionality is planned, but until it's not implemented, here are some tips how to set it up manually.

## Windows

### Bat file called from a vbs script

[inobrevi](https://github.com/inobrevi)'s solution from [here](https://github.com/richibrics/IoTuring/issues/94#issuecomment-2002548352):

After configuring IoTuring, you can create a `IoTuring.bat` file:

```
@echo off
python -m IoTuring
```

And then run it from `IoTuring_hidden.vbs` script, which would run it without showing console window:

```
CreateObject("Wscript.Shell").Run "IoTuring.bat",0,True
```

Save both files in the same folder, run `IoTuring_hidden.vbs` and it just works.

You can also add this .vbs script to autorun

### NSSM

With nssm it's possible to create a service for any command: https://nssm.cc

## Linux

### As a user service with Systemd (recommended)

Example service file is here: [IoTuring.service](IoTuring.service)

Install the service:

<!-- 
TODO: use this path as regular install in the future:
sudo cp docs/IoTuring.service /usr/lib/systemd/user/ 
-->
```shell
mkdir -p ~/.local/share/systemd/user/
cp docs/IoTuring.service ~/.local/share/systemd/user/

systemctl --user daemon-reload
systemctl --user edit IoTuring.service
```

Add to the override:

```ini
[Service]
# Select start command according to installation:
# system wide installation:
ExecStart=IoTuring
# Pipx:
ExecStart=pipx run IoTuring
# Venv:
ExecStart=/path/to/IoTuring/.venv/bin/IoTuring
```
Enable and start the service:

```shell
systemctl --user enable IoTuring.service
systemctl --user start IoTuring.service
```

#### Start user service before login

This is optional. Without this, IoTuring starts after login.

```shell
# Enable the automatic login of the user, so IoTuring can start right after boot:
loginctl enable-linger $(whoami)

# Copy the service which restarts IoTuring:
cp docs/IoTuring-restart.service ~/.local/share/systemd/user/

systemctl --user daemon-reload
systemctl --user enable IoTuring-restart.service
systemctl --user start IoTuring-restart.service
```

### As a system service with Systemd

Some entities may not work if installed as a system service

Example service file is here: [IoTuring.service](IoTuring.service)

Install the service:

```shell
sudo cp docs/IoTuring.service /usr/lib/systemd/system/

sudo systemctl daemon-reload
sudo systemctl edit IoTuring.service
```

Add to the override:

```ini
[Service]
# User and group to run as:
User=user
Group=group

# Select start command according to installation:
# system wide installation:
ExecStart=IoTuring
# Pipx:
ExecStart=pipx run IoTuring
# Venv:
ExecStart=/path/to/IoTuring/.venv/bin/IoTuring
```

Enable and start the service:

```shell
sudo systemctl enable IoTuring.service
sudo systemctl start IoTuring.service
```