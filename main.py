from App.App import App
from Entity.Deployments.Username.Username import Username
from Logger.Logger import Logger
from Entity.Entity import Entity
from Warehouse.Warehouse import Warehouse

if __name__ == "__main__":
    logger = Logger() # Unique init of Logger. Then I will use Logger.getInstance() to get this instance
    
    logger.Log(Logger.LOG_INFO,"App",App()) # Print App info
    
    wh = Warehouse()
    wh.AddEntity(Username())

    exit(0)