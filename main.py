from MyApp.App import App
from Configurator.Configurator import Configurator
from Configurator.ConfiguratorLoader import ConfiguratorLoader
from Entity.Deployments.Username.Username import Username
from Entity.EntityManager import EntityManager
from Logger.Logger import Logger
from Entity.Entity import Entity
from Warehouse.Deployments.ConsoleWarehouse.ConsoleWarehouse import ConsoleWarehouse
from Warehouse.Warehouse import Warehouse
import sys

warehouses = []
entities =  []

if __name__ == "__main__":
    configurator = Configurator()

    if len(sys.argv)>1 and sys.argv[1]=="-c": # add -c to configure with the menu
        configurator.Menu()

    logger = Logger.getInstance() # I use .getInstance() to init/get this instance 'cause it's a singleton
    logger.Log(Logger.LOG_INFO,"App",App()) # Print App info

    eM = EntityManager.getInstance() # I use .getInstance() to init/get this instance 'cause it's a singleton
    
    # These will be done from the configuration reader
    warehouses = ConfiguratorLoader(configurator).LoadWarehouses()
    entities =  ConfiguratorLoader(configurator).LoadEntities()

    # Add entites to the EntityManager
    for entity in entities:
        eM.AddActiveEntity(entity)
    
    # Ready to start Entities loop
    eM.Start()
    
    # Prepare  warehouses
    for warehouse in warehouses:
        warehouse.Start()
    
    
    logger.Log(Logger.LOG_DEBUG, "Main", "Main finished its work ;)")
    exit(0)