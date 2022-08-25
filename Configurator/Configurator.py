import inspect  # To get this folder path and reach the configurations file
import os  # Configurations file path manipulation
import json
from Logger.LogObject import LogObject

from ClassManager.EntityClassManager import EntityClassManager
from ClassManager.WarehouseClassManager import WarehouseClassManager

from Configurator.MenuPreset import MenuPreset

BLANK_CONFIGURATION = {'active_entities': [{"type": "AppInfo"}], 'active_warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"

KEY_WAREHOUSE_TYPE = "type"

KEY_ENTITY_TYPE = "type"
KEY_ENTITY_TAG = "tag"

SEPARATOR_CHAR_NUMBER = 150

class Configurator(LogObject):
    # Must be in the same folder of this file
    configurations_filename = "configurations.json"

    def __init__(self) -> None:
        self.config = None
        self.LoadConfigurations()

    def GetConfigurations(self):
        """ Return a copy of the configurations dict"""
        return self.config.copy() # Safe return

    def Menu(self) -> None:
        """ UI for Entities and Warehouses settings """
        run_app = False
        while(not run_app):
            self.PrintSeparator()
            print("1 - Manage entities")
            print("2 - Manage warehouses")
            print("C - Start IoTuring")
            print("Q - Quit\n")

            choice = False
            while not choice:
                choice = input("Select your choice: ")
                if choice == "1":
                    choice = True  # Valid choice
                    self.ManageEntities()
                elif choice == "2":
                    choice = True  # Valid choice
                    self.ManageWarehouses()
                elif choice == "c" or choice == "C":
                    choice = True   # Valid choice
                    run_app = True # Will start the program exiting from here
                    print("") # Blank line
                    self.WriteConfigurations()
                elif choice == "q" or choice == "Q":
                    self.WriteConfigurations()
                    exit(0)
                else:
                    print("Invalid choice")
                    choice = False

    def ManageEntities(self) -> None:
        """ UI for Entities settings """
        ecm = EntityClassManager()
        while(True):
            choice = False
            while not choice:
                self.PrintSeparator()
                print("Active entities: (enter the entity number to edit its configuration or to disable it)")
                i=0
                for entity in self.config[KEY_ACTIVE_ENTITIES]:
                    if not KEY_ENTITY_TAG in entity:
                        print(i+1,"-",entity[KEY_ENTITY_TYPE])
                    else:
                        print(i+1,"-",entity[KEY_ENTITY_TYPE] , "with tag" , entity[KEY_ENTITY_TAG])
                    i+=1
                print("\nA - Add a new entity")
                print("Q - Come back")
                choice = input("\nSelect your choice: ")
                try:
                    if choice == 'a' or choice == 'A':
                        choice = True
                        self.SelectNewEntity(ecm) 
                    elif choice == "q" or choice == "Q":
                        return
                    else:
                        choice = int(choice) # If not valid I have a ValueError
                        choice = choice - 1 # So now chosen entity = active entity in configurations
                        if choice >= 0 and choice < len(self.config[KEY_ACTIVE_ENTITIES]):
                            self.ManageSingleEntity(self.config[KEY_ACTIVE_ENTITIES][choice],ecm) 
                            choice = True
                        else:
                            raise ValueError()
                except ValueError:
                    choice = False
                    print("Please insert a valid choice")
                except Exception as e:
                    choice = False
                    self.Log(self.LOG_ERROR,"Error in Entity select menu: " + str(e))


    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = WarehouseClassManager()
        
        while(True):
            self.PrintSeparator()
            print("Select the warehouse you want to manage (X for enabled):")
            availableWarehouses = wcm.ListAvailableClassesNames()
            for index, whName in enumerate(availableWarehouses):
                if not self.IsWarehouseActive(whName.replace("Warehouse","")):
                    print("[ ] " + str(index+1) + " - " + whName.replace("Warehouse",""))
                else:
                    print("[X] " + str(index+1) + " - " + whName.replace("Warehouse",""))
            print("    Q - Come back\n")
            choice = False
            while not choice:
                choice = input("Which one do you want to manage ? ")
                if choice == "q" or choice == "Q":
                    return
                else: 
                    try:
                        choice = int(choice) - 1
                        if choice >= 0 and choice < len(availableWarehouses):
                            self.ManageSingleWarehouse(availableWarehouses[choice].replace("Warehouse",""),wcm)
                            choice = True
                        else:
                            raise IndexError("Choice out of warehouses range")
                    except IndexError:
                        choice = False
                        print("Please insert a valid Warehouse index")
                    except Exception as e:
                        choice = False
                        self.Log(self.LOG_ERROR,"Error in Warehouse select menu: " + str(e))

    def LoadConfigurations(self) -> None:
        """ Load into a dict in self the configurations file in this script's folder """
        thisFolder = os.path.dirname(inspect.getfile(Configurator))
        path = os.path.join(thisFolder, self.configurations_filename)
        try:
            with open(path, "r") as f:
                self.config = json.loads(f.read())
        except:
            self.config = BLANK_CONFIGURATION
    
        # check valid keys
        if not KEY_ACTIVE_ENTITIES in self.config or not KEY_ACTIVE_WAREHOUSES in self.config:
            self.Log(self.LOG_ERROR, "Invalid configurations, you may have broken them manually. Check you have a dict like this in your configurations file (or delete it to generate a new one) : ")
            self.Log(self.LOG_ERROR, BLANK_CONFIGURATION)
            exit(1)

    def WriteConfigurations(self) -> None:
        """ Save to configurations file in this script's folder the dict in self"""
        thisFolder = os.path.dirname(inspect.getfile(Configurator))
        path = os.path.join(thisFolder, self.configurations_filename)
        with open(path, "w") as f:
            f.write(json.dumps(self.config))

    def ManageSingleWarehouse(self, warehouseName, wcm: WarehouseClassManager):
        """ UI for single Warehouse settings """
        print("\nWhat do you want to do with " + warehouseName + "?")
        if self.IsWarehouseActive(warehouseName):
            print("E - Edit the warehouse settings")
            print("R - Remove the warehouse")
        else:
            print("A - Add the warehouse")
        print("Q - Come back")

        choice = input("Select an operation: ")
        
        if self.IsWarehouseActive(warehouseName):
            if choice == "r" or choice == "R":
                if(Configurator.ConfirmQuestion()):
                    self.RemoveActiveWarehouse(warehouseName)
            elif choice == "e" or choice == "E":
                self.EditActiveWarehouse(warehouseName,wcm)
        else:
            if choice == "a" or choice == "A":
                self.AddActiveWarehouse(warehouseName,wcm)

    def ManageSingleEntity(self, entityConfig, ecm:EntityClassManager):
        """ UI to manage an active warehouse (edit config/remove) """
        choice = False
        while(not choice):
            self.PrintSeparator()
            print("What do you want to do with " + entityConfig[KEY_ENTITY_TYPE] + "?")
            print("\nE - Edit the entity settings")
            print("R - Remove the entity")
            print("Q - Come back")

            choice = input("Select an operation: ")
            
            if choice == "r" or choice == "R":
                if(Configurator.ConfirmQuestion()):
                    self.RemoveActiveEntity(entityConfig,ecm)
            elif choice == "e" or choice == "E":
                self.EditActiveEntity(entityConfig,ecm)

    def SelectNewEntity(self, ecm: EntityClassManager):
        """ UI to add a new Entity """
        choice = False
        while not choice:
            entityList = ecm.ListAvailableClassesNames()
            # Now I remove the entities that are active and that do not allow multi instances
            for activeEntity in self.config[KEY_ACTIVE_ENTITIES]:
                if not ecm.GetClassFromName(activeEntity[KEY_ENTITY_TYPE]).AllowMultiInstance():
                    entityList.remove(activeEntity[KEY_ENTITY_TYPE])

            # Print entities with their index in order to choose them
            self.PrintSeparator()
            print("Available entities: ")
            print("PS: if you don't see the entity you want, it may be already active and may not accept another version of itself)\n")
            i=0
            for entity in entityList:
                print(i+1,"-",entity)
                i+=1        
                
            print("\nQ - Come back")

            choice = input("\nSelect your choice: ")
            try:
                if choice == "q" or choice == "Q":
                    return
                else: 
                    choice = int(choice) # If not valid I have a ValueError
                    choice = choice - 1 # So now chosen entity = active entity in configurations
                    if choice >= 0 and choice < len(entityList):
                        # Use the entity name to get the menupreset and configure it
                        self.AddActiveEntity(entityList[choice],ecm)
                        choice = True
                    else:
                        raise ValueError()
            except ValueError:
                choice = False
                print("Please insert a valid choice")
            except Exception as e:
                choice = False
                self.Log(self.LOG_ERROR,"Error in Entity select menu: " + str(e))

    def AddActiveEntity(self, entityName, ecm: EntityClassManager):
        """ From entity name, get its class and retrieve the configuration preset, then add to configuration dict """
        entityClass = ecm.GetClassFromName(entityName)
        try:
            preset = entityClass.ConfigurationPreset()

            if preset is not None: # Then let's configure the Entity
                # Ask also for Tag if the entity allows multi-instance
                if entityClass.AllowMultiInstance():
                    preset.AddTagQuestion()
                    
                preset.PrintRules()
                for index, question in enumerate(preset.ListEntries()):
                    preset.Question(index)
                
            else:
                preset = MenuPreset() # Use blank
                print("No configuration needed for this Entity :)")

            self.EntityMenuPresetToConfiguration(entityName,preset)
        except Exception as e:
            print("Error during entity preset loading: " + str(e))

    def IsEntityActive(self, entityName) -> bool:
        """ Return True if an Entity is active """
        for entity in self.config[KEY_ACTIVE_ENTITIES]:
            if entityName == entity[KEY_ENTITY_TYPE]:
                return True
        return False 

    def RemoveActiveEntity(self, entityConfig, ecm:EntityClassManager) -> None:
        """ Remove entity name from the list of active entities if present """
        # TODO Check if no dependencies from it

        for activeEntity in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
            if activeEntity != entityConfig:
                # Get class from entity type
                entityClass = ecm.GetClassFromName(activeEntity[KEY_ENTITY_TYPE])
                # Retrieve entity dependencies
                deps = entityClass.GetDependenciesList()
                # Check if entity I want to remove is dependent from the entity I'm iterating
                if entityConfig[KEY_ENTITY_TYPE] in deps:
                    raise Exception("Can't remove this entity because "  + activeEntity[KEY_ENTITY_TYPE] + " depends from it :(")


        if entityConfig in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].remove(entityConfig)

    def IsWarehouseActive(self, warehouseName) -> bool:
        """ Return True if a warehouse is active """
        for wh in self.config[KEY_ACTIVE_WAREHOUSES]:
            if warehouseName == wh[KEY_WAREHOUSE_TYPE]:
                return True
        return False 

    def AddActiveWarehouse(self, warehouseName, wcm: WarehouseClassManager) -> None:
        """ Add warehouse to the preferences using a menu with the warehouse preset if available """

        whClass = wcm.GetClassFromName(warehouseName + "Warehouse")
        try:
            preset = whClass.ConfigurationPreset() # With the use of "type" I get the staticmethod of the subclass and not of the parentclass
            
            if preset is not None:
                preset.PrintRules()

                for index, question in enumerate(preset.ListEntries()):
                    preset.Question(index)
            else:
                preset = MenuPreset() # Use blank
                print("No configuration needed for this Warehouse :)")
            
            # Save added settings
            self.WarehouseMenuPresetToConfiguration(warehouseName,preset)
        except Exception as e:
            print("Error during warehouse preset loading: " + str(e))

    def EditActiveWarehouse(self, warehouseName, wcm: WarehouseClassManager) -> None:
        """ UI for single Warehouse settings edit """
        print("You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")
        # WarehouseMenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to read it later
        # TO implement only when I know how to add removable value while editing configurations
        pass # TODO Implement

    def EditActiveEntity(self, entityConfig, ecm: WarehouseClassManager) -> None:
        """ UI for single Entity settings edit """
        print("You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")
        pass # TODO Implement
   
    def RemoveActiveWarehouse(self, warehouseName) -> None:
        """ Remove warehouse name from the list of active warehouses if present """
        for wh in self.config[KEY_ACTIVE_WAREHOUSES]:
            if warehouseName == wh[KEY_WAREHOUSE_TYPE]:
                # I remove this wh from the list
                self.config[KEY_ACTIVE_WAREHOUSES].remove(wh)
                return

    def WarehouseMenuPresetToConfiguration(self,whName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict in warehouse part """
        _dict = preset.GetDict()
        _dict[KEY_WAREHOUSE_TYPE] = whName.replace("Warehouse","")
        self.config[KEY_ACTIVE_WAREHOUSES].append(_dict)
        print("Configuration added for \""+whName+"\" :)")

    def EntityMenuPresetToConfiguration(self,entityName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict in entity part """
        _dict = preset.GetDict()
        _dict[KEY_ENTITY_TYPE] = entityName
        self.config[KEY_ACTIVE_ENTITIES].append(_dict)
        print("Configuration added for \""+entityName+"\" :)")

    def CheckDependencies(self,entity, entityClassManager: EntityClassManager):
        """ Return True if there aren't entities that must be loaded before the passed one """
        # Each entity has a dependency list. If all those dependencies are already active, I return True so the current entity can be activated
        entityClass = entityClassManager.GetClassFromName(entity)
        for dependency in entityClass.GetDependenciesList():
            if dependency not in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
                return False
        return True

    def PrintDependencyError(self,entity, entityClassManager: EntityClassManager):
        """ Run only if if self.CheckDependencies returned False. 
            Prints a message with the dependencies the user has to activate before activating this entity """

        print("!!! You can't activate this Entity. Please activate the following entities in order to use this one: !!!\n")

        entityClass = entityClassManager.GetClassFromName(entity)
        for dependency in entityClass.GetDependenciesList():
            if dependency not in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
                print("---> " + dependency + " <----")

        print("\nThank you for the attention")

    def PrintSeparator(self):
        print("\n"+SEPARATOR_CHAR_NUMBER*'#')

    @staticmethod
    def ConfirmQuestion():
        value = input("You sure ? [y/n] ")
        if value == "y" or value == "Y":
            return True
        else:
            return False