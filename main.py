from App.App import App
from Logger.Logger import Logger
from Entity.Entity import Entity

if __name__ == "__main__":
    logger = Logger() # Unique init of Logger. Then I will use Logger.getInstance() to get this instance
    
    logger.Log(Logger.LOG_INFO,"App",App()) # Print App info
    
    Entity()

    exit(0)