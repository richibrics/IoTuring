from App.App import App
from Entity.Deployments.Username.Username import Username
from Entity.EntityManager import EntityManager
from Logger.Logger import Logger
from Entity.Entity import Entity
from Warehouse.Console.Console_Warehouse import Console_Warehouse
from Warehouse.Warehouse import Warehouse

warehouses = []

if __name__ == "__main__":
    logger = Logger() # Unique init of Logger. Then I will use Logger.getInstance() to get this instance
    logger.Log(Logger.LOG_INFO,"App",App()) # Print App info
    eM = EntityManager()
    
    # These will be done from the configuration reader
    warehouses.append(Console_Warehouse())
    warehouses[0].AddEntity(eM.NewEntity(eM.EntityNameToClass("Username")).getInstance())
    for wh in warehouses:
        wh.Start()

    eM.Start()
    
    logger.Log(Logger.LOG_DEBUG, "Main", "Main finished its work ;)")
    exit(0)