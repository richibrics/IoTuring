#!/usr/bin/env python3

from IoTuring.MyApp.App import App
from IoTuring.Configurator.Configurator import Configurator
from IoTuring.Configurator.ConfiguratorLoader import ConfiguratorLoader
from IoTuring.Entity.EntityManager import EntityManager
from IoTuring.Logger.Logger import Logger
from IoTuring.Logger.Colors import Colors
import sys
import signal
import os
import time

warehouses = []
entities = []


def loop():
    signal.signal(signal.SIGINT, Exit_SIGINT_handler)
    
    # Start logger:
    logger = Logger()
    configurator = Configurator()

    # add -c to configure with the menu
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        if not configurator.configuratorIO.checkConfigurationFileExists(): 
            # If the file doesn't exist, check if it's in the old location
            configurator.configuratorIO.checkConfigurationFileInOldLocation()
        configurator.Menu()

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
    while(True):
        time.sleep(1)

def Exit_SIGINT_handler(sig, frame):
    logger = Logger()
    logger.Log(Logger.LOG_INFO, "Main", "Application closed by SigInt", printToConsole=False) # to file
    
    messages = ["Exiting...",
                "Thanks for using IoTuring !"]
    print("") # New line
    for message in messages:
        text = ""
        if(Logger.checkTerminalSupportsColors()):
            text += Colors.cyan
        text += message 
        if(Logger.checkTerminalSupportsColors()):
            text += Colors.reset
        logger.Log(Logger.LOG_INFO, "Main", text, writeToFile=False) # to terminal
        
    logger.CloseFile()
    os._exit(0)