import inspect  # To get this folder path and reach the configurations file
import os  # Configurations file path manipulation
import json
from Logger.LogObject import LogObject

from ClassManager.EntityClassManager import EntityClassManager
from ClassManager.WarehouseClassManager import WarehouseClassManager

from Configurator.MenuPreset import MenuPreset

BLANK_CONFIGURATION = {'active_entities': [], 'warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"

KEY_WAREHOUSE_TYPE = "type"

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
            print("\n1 - Select entities")
            print("2 - Manage warehouses")
            print("C - Start DomoticTuring")
            print("Q - Quit\n")

            choice = False
            while not choice:
                choice = input("Select your choice: ")
                if choice == "1":
                    self.SelectEntities()
                elif choice == "2":
                    self.ManageWarehouses()
                elif choice == "c" or choice == "C":
                    choice = True  # Will start the program exiting from here
                    run_app = True
                    print("") # Blank line
                    self.WriteConfigurations()
                elif choice == "q" or choice == "Q":
                    self.WriteConfigurations()
                    exit(0)
                else:
                    print("Invalid choice")
                    choice = False

    def SelectEntities(self) -> None:
        """ UI for Entities settings """
        ecm = EntityClassManager()
        while(True):
            print("\nSelect your entities (X for enabled):")
            availableEntities = ecm.ListAvailableClassesNames()
            for index, entityName in enumerate(availableEntities):
                if not self.IsEntityActive(entityName):
                    print("[ ] " + str(index+1) + " - " + entityName)
                else:
                    print("[X] " + str(index+1) + " - " + entityName)
            print("    Q - Come back\n")
            choice = False
            while not choice:
                choice = input("Which one do you want to enable/disable ? ")
                if choice == "q" or choice == "Q":
                    return
                else: 
                    try:
                        choice = int(choice) -1
                        if choice >= 0 and choice < len(availableEntities):
                            # I have the choice
                            if self.IsEntityActive(availableEntities[choice]):
                                # Disable it (remove from active entities list)
                                self.RemoveActiveEntity(availableEntities[choice])
                            else:
                                # Enable it (add to active entities list) if all dep entity are active, otherwise tell which dependencies must be actived before
                                if self.CheckDependencies(availableEntities[choice],ecm):
                                    self.AddActiveEntity(availableEntities[choice])
                                else:
                                    self.PrintDependencyError(availableEntities[choice],ecm)
                            choice = True
                        else:
                            raise IndexError("Choice out of entities range")
                    except IndexError:
                        choice = False
                        print("Please insert a valid Entity index")
                    except Exception as e:
                        choice = False
                        self.Log(self.LOG_ERROR,"Error in Entity select menu: " + str(e))


    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = WarehouseClassManager()
        
        while(True):
            print("\nSelect the warehouse you want to manage (X for enabled):")
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
                self.RemoveActiveWarehouse(warehouseName)
            elif choice == "e" or choice == "E":
                self.EditActiveWarehouse(warehouseName,wcm)
        else:
            if choice == "a" or choice == "A":
                self.AddActiveWarehouse(warehouseName,wcm)

    def IsEntityActive(self, entityName) -> bool:
        """ Return True if an Entity is active """
        return entityName in self.config[KEY_ACTIVE_ENTITIES]

    def AddActiveEntity(self, entityName) -> None:
        """ Add entity name to the list of active entities if not already present """
        if not entityName in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].append(entityName)
   
    def RemoveActiveEntity(self, entityName) -> None:
        """ Remove entity name from the list of active entities if present """
        if entityName in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].remove(entityName)

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
            print(whClass.ConfigurationPreset)
            preset = whClass.ConfigurationPreset() # With the use of "type" I get the staticmethod of the subclass and not of the parentclass
            
            if preset is not None:
                print("\n\t-- Rules --")
                print("\t\tIf you see {!} then the value is complusory")
                print("\t\tIf you see [*] then the value in the brackets is the default one: leave blank the input to use that value")
                print("\t-- End of rules --\n")

                for index, question in enumerate(preset.ListEntries()):
                    preset.Question(index)
            else:
                preset = MenuPreset() # Use blank
                print("No configuration available for this Warehouse :)")
            
            # Save added settings
            self.MenuPresetToConfiguration(warehouseName,preset)
        except Exception as e:
            print("Error during preset loading: " + str(e))

    def EditActiveWarehouse(self, warehouseName, wcm: WarehouseClassManager) -> None:
        """ UI for single Warehouse settings edit """
        print("You can't do that at the moment bro")
        # MenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to readd it later
        # TO implement only when I know how to add removable value while editing configurations
        pass # TODO Implement
   
    def RemoveActiveWarehouse(self, warehouseName) -> None:
        """ Remove warehouse name from the list of active warehouses if present """
        for wh in self.config[KEY_ACTIVE_WAREHOUSES]:
            if warehouseName == wh[KEY_WAREHOUSE_TYPE]:
                # I remove this wh from the list
                self.config[KEY_ACTIVE_WAREHOUSES].remove(wh)
                return

    def MenuPresetToConfiguration(self,whName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict """
        _dict = preset.GetDict()
        _dict[KEY_WAREHOUSE_TYPE] = whName.replace("Warehouse","")
        self.config[KEY_ACTIVE_WAREHOUSES].append(_dict)
        print("Configuration added for \""+whName+"\" :)")

    def CheckDependencies(self,entity, entityClassManager: EntityClassManager):
        """ Return True if there aren't entities that must be loaded before the passed one """
        # Each entity has a dependency list. If all those dependencies are already active, I return True so the current entity can be activated
        entityClass = entityClassManager.GetClassFromName(entity)
        for dependency in entityClass.GetDependenciesList():
            if dependency not in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
                return False
        return True

    def PrintDependencyError(self,entity, entityClassManager: EntityClassManager):
        """ Run only if if self.CheckDependencies returned False. Print a message with the dependencies to activate before activating this entity """

        print("!!! You can't activate this Entity. Please activate the following entities in order to use this one: !!!\n")

        entityClass = entityClassManager.GetClassFromName(entity)
        for dependency in entityClass.GetDependenciesList():
            if dependency not in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
                print("---> " + dependency + " <----")

        print("\nThank you for the attention")
