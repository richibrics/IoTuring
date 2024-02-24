#!/usr/bin/env python3

import signal
import sys
import time
import argparse

from IoTuring.MyApp.App import App
from IoTuring.Configurator.Configurator import Configurator
from IoTuring.Configurator.ConfiguratorLoader import ConfiguratorLoader
from IoTuring.Entity.EntityManager import EntityManager
from IoTuring.Logger.Logger import Logger
from IoTuring.Logger.Colors import Colors
from IoTuring.Settings.SettingsManager import SettingsManager

warehouses = []
entities = []


def loop():

    parser = argparse.ArgumentParser(
        prog=App.getName(),
        description=App.getDescription(),
        epilog="Start without argument for normal use"
    )

    parser.add_argument("-v", "--version",
                        action="version",
                        version=f"{App.getName()} {App.getVersion()}"
                        )

    parser.add_argument("-c", "--configurator",
                        help="enter configuration mode",
                        action="store_true")

    parser.add_argument("-o", "--open-config",
                        help="open config file",
                        action="store_true")

    args = parser.parse_args()

    # Only one argument should be used:
    if all(vars(args).values()):
        parser.print_help()
        print()
        sys.exit("Error: Invalid arguments!")

    # Clear the terminal
    Configurator.ClearTerminal()

    # Start logger:
    logger = Logger()
    configurator = Configurator()

    # Load Logger settings before everything:
    ConfiguratorLoader(configurator).LoadSettings()

    logger.Log(Logger.LOG_DEBUG, "App", f"Selected options: {vars(args)}")

    if args.configurator:
        try:
            # Check old location:
            configurator.CheckFile()

            configurator.Menu()
        except KeyboardInterrupt:
            logger.Log(Logger.LOG_WARNING, "Configurator",
                       "Configuration NOT saved")
            Exit_SIGINT_handler()

    elif args.open_config:
        configurator.OpenConfigInEditor()
        sys.exit(0)

    # This have to start after configurator.Menu(), otherwise won't work starting from the menu
    signal.signal(signal.SIGINT, Exit_SIGINT_handler)

    # Load Settings:
    settings = ConfiguratorLoader(configurator).LoadSettings()
    sM = SettingsManager()
    sM.AddSettings(settings)

    logger.Log(Logger.LOG_INFO, "App", App())  # Print App info

    # Add help if not started from Configurator
    if not args.configurator:
        logger.Log(Logger.LOG_INFO, "Configurator",
                   "Run the script with -c to enter configuration mode")

    # These will be done from the configuration reader
    entities = ConfiguratorLoader(configurator).LoadEntities()
    warehouses = ConfiguratorLoader(configurator).LoadWarehouses()

    # Add entites to the EntityManager
    eM = EntityManager()
    for entity in entities:
        eM.AddActiveEntity(entity)

    # Ready to start Entities loop
    eM.Start()

    # Prepare warehouses -  # after entities, so entitites have already told to which EntityCommand I need to subscribe !
    for warehouse in warehouses:
        warehouse.Start()

    logger.Log(Logger.LOG_DEBUG, "Main", "Main finished its work ;)")

    # Threads are in daemon mode (entities and warehouses) because
    # on Windows a SIGINT signal can't be catched otherwise.
    # Daemon mode involves thread exit when main ends. So
    # I need main to never end
    while (True):
        time.sleep(1)


def Exit_SIGINT_handler(sig=None, frame=None):
    logger = Logger()
    logger.Log(Logger.LOG_INFO, "Main", "Application closed by SigInt",
               printToConsole=False)  # to file

    print()  # New line
    goodByeMessage = "Exiting...\nThanks for using IoTuring !"
    logger.Log(Logger.LOG_INFO, "Main", goodByeMessage,
               writeToFile=False, color=Colors.cyan)  # to terminal

    logger.CloseFile()
    sys.exit(0)
