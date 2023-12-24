#!/usr/bin/env python3

from IoTuring.MyApp.App import App
from IoTuring.Configurator.Configurator import Configurator
from IoTuring.Configurator.ConfiguratorLoader import ConfiguratorLoader
from IoTuring.Entity.EntityManager import EntityManager
from IoTuring.Logger.Logger import Logger
from IoTuring.Logger.Colors import Colors
import signal
import os
import time
import argparse

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
        print("error: use only one option!", end="\n\n")
        parser.print_help()
        os._exit(0)

    # Clear the terminal
    Configurator.ClearTerminal()

    # Start logger:
    logger = Logger()
    configurator = Configurator()

    logger.Log(Logger.LOG_DEBUG, "App", f"Selected options: {vars(args)}")

    if args.configurator:
        try:
            # Check old location:
            configurator.CheckFile()

            configurator.Menu(clear_screen=False)
        except KeyboardInterrupt:
            logger.Log(Logger.LOG_WARNING, "Configurator",
                       "Configuration NOT saved")
            Exit_SIGINT_handler()

    elif args.open_config:
        configurator.OpenConfigInEditor()
        os._exit(0)

    # This have to start after configurator.Menu(), otherwise won't work starting from the menu
    signal.signal(signal.SIGINT, Exit_SIGINT_handler)

    logger.Log(Logger.LOG_INFO, "App", App())  # Print App info
    logger.Log(Logger.LOG_INFO, "Configurator",
               "Run the script with -c to enter configuration mode")

    eM = EntityManager()

    # These will be done from the configuration reader
    entities = ConfiguratorLoader(configurator).LoadEntities()
    warehouses = ConfiguratorLoader(configurator).LoadWarehouses()

    # Add entites to the EntityManager
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

    messages = ["Exiting...",
                "Thanks for using IoTuring !"]
    print()  # New line
    for message in messages:
        text = ""
        if (Logger.checkTerminalSupportsColors()):
            text += Colors.cyan
        text += message
        if (Logger.checkTerminalSupportsColors()):
            text += Colors.reset
        logger.Log(Logger.LOG_INFO, "Main", text,
                   writeToFile=False)  # to terminal

    logger.CloseFile()
    os._exit(0)
