#!/usr/bin/env python3

from IoTuring.MyApp.App import App
from IoTuring.Configurator.Configurator import Configurator
from IoTuring.Configurator.ConfiguratorLoader import ConfiguratorLoader
from IoTuring.Entity.Deployments.Username.Username import Username
from IoTuring.Entity.EntityManager import EntityManager
from IoTuring.Logger.Logger import Logger, Colors
from IoTuring.Entity.Entity import Entity
from IoTuring.Warehouse.Deployments.ConsoleWarehouse.ConsoleWarehouse import ConsoleWarehouse
from IoTuring.Warehouse.Warehouse import Warehouse
import sys
import signal
import os

warehouses = []
entities = []


def loop():
    signal.signal(signal.SIGINT, signal_handler)
    
    # I use .getInstance() to init/get this instance 'cause it's a singleton
    logger = Logger.getInstance()

    configurator = Configurator()

    # add -c to configure with the menu
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        configurator.Menu()

    logger.Log(Logger.LOG_INFO, "App", App())  # Print App info
    logger.Log(Logger.LOG_INFO, "Configurator",
               "Run the script with -c to enter configuration mode")

    # I use .getInstance() to init/get this instance 'cause it's a singleton
    eM = EntityManager.getInstance()

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

def signal_handler(sig, frame):
    print("") # New line
    Logger.getInstance().Log(Logger.LOG_INFO, "Main", Colors.cyan + 'Exiting...' + Colors.reset)
    Logger.getInstance().Log(Logger.LOG_INFO, "Main", Colors.cyan + 'Thanks for using IoTuring !' + Colors.reset)
    os._exit(0)