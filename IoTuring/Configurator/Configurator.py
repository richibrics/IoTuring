from IoTuring.Logger.LogObject import LogObject

from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager

from IoTuring.Configurator import ConfiguratorIO

# TODO Find new location for this message
HELP_MESSAGE = f"""
You can find the configuration file in the following path: 
\tmacOS\t\t~/Library/Application Support/IoTuring/configurations.json 
\tLinux\t\t~/.config/IoTuring/configurations.json 
\tWindows\t\t%APPDATA%/IoTuring/configurations.json
\tFallback\t[ioturing_install_path]/Configurator/configurations.json

You can also set your preferred directory by setting the environment variable {ConfiguratorIO.CONFIG_PATH_ENV_VAR} 
Configuration will be stored there in the file configurations.json.
"""


BLANK_CONFIGURATION = {'active_entities': [
    {"type": "AppInfo"}], 'active_warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"

KEY_WAREHOUSE_TYPE = "type"

KEY_ENTITY_TYPE = "type"
KEY_ENTITY_TAG = "tag"

SEPARATOR_CHAR_NUMBER = 120

class Configurator(LogObject):

    def __init__(self) -> None:
        self.configuratorIO = ConfiguratorIO.ConfiguratorIO()
        self.config = self.LoadConfigurations()

    def GetConfigurations(self) -> dict:
        """ Return a copy of the configurations dict"""
        return self.config.copy()  # Safe return

    def Menu(self) -> None:
        """ UI for Entities and Warehouses settings """
        run_app = False
        while(not run_app):
            self.PrintSeparator()
            print("1 - Manage entities")
            print("2 - Manage warehouses")
            print("C - Start IoTuring")
            print("H - Help")
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
                    run_app = True  # Will start the program exiting from here
                    print("")  #  Blank line
                    self.WriteConfigurations()
                elif choice == "q" or choice == "Q":
                    self.WriteConfigurations()
                    exit(0)
                elif choice == "h" or choice == "H":
                    print(HELP_MESSAGE)
                    choice = False
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
                print(
                    "Active entities: (enter the entity number to edit its configuration or to disable it)")
                i = 0
                for entity in self.config[KEY_ACTIVE_ENTITIES]:
                    if not KEY_ENTITY_TAG in entity:
                        print(i+1, "-", entity[KEY_ENTITY_TYPE])
                    else:
                        print(i+1, "-", entity[KEY_ENTITY_TYPE],
                              "with tag", entity[KEY_ENTITY_TAG])
                    i += 1
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
                        # If not valid I have a ValueError
                        choice = int(choice)
                        choice = choice - 1  # So now chosen entity = active entity in configurations
                        if choice >= 0 and choice < len(self.config[KEY_ACTIVE_ENTITIES]):
                            self.ManageSingleEntity(
                                self.config[KEY_ACTIVE_ENTITIES][choice], ecm)
                            choice = True
                        else:
                            raise ValueError()
                except ValueError:
                    choice = False
                    print("Please insert a valid choice")
                except Exception as e:
                    choice = False
                    self.Log(self.LOG_ERROR,
                             "Error in Entity select menu: " + str(e))

    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = WarehouseClassManager()

        while(True):
            self.PrintSeparator()
            print("Select the warehouse you want to manage (X for enabled):")
            availableWarehouses = wcm.ListAvailableClassesNames()
            for index, whName in enumerate(availableWarehouses):
                if not self.IsWarehouseActive(whName.replace("Warehouse", "")):
                    print("[ ] " + str(index+1) + " - " +
                          whName.replace("Warehouse", ""))
                else:
                    print("[X] " + str(index+1) + " - " +
                          whName.replace("Warehouse", ""))
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
                            self.ManageSingleWarehouse(
                                availableWarehouses[choice].replace("Warehouse", ""), wcm)
                            choice = True
                        else:
                            raise IndexError("Choice out of warehouses range")
                    except IndexError:
                        choice = False
                        print("Please insert a valid Warehouse index")
                    except Exception as e:
                        choice = False
                        self.Log(self.LOG_ERROR,
                                 "Error in Warehouse select menu: " + str(e))

    def LoadConfigurations(self) -> dict:
        """ Reads the configuration file and returns configuration dictionary.
            If not available, returns the blank configuration  """
        read_config = self.configuratorIO.readConfigurations()
        if read_config is None:
            read_config = BLANK_CONFIGURATION
        return read_config

    def WriteConfigurations(self) -> None:
        """ Save to configurations file """
        self.configuratorIO.writeConfigurations(self.config)

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
                self.EditActiveWarehouse(warehouseName, wcm)
        else:
            if choice == "a" or choice == "A":
                self.AddActiveWarehouse(warehouseName, wcm)

    def ManageSingleEntity(self, entityConfig, ecm: EntityClassManager):
        """ UI to manage an active warehouse (edit config/remove) """
        choice = False
        while(not choice):
            self.PrintSeparator()
            print("What do you want to do with " +
                  entityConfig[KEY_ENTITY_TYPE] + "?")
            print("\nE - Edit the entity settings")
            print("R - Remove the entity")
            print("Q - Come back")

            choice = input("Select an operation: ")

            if choice == "r" or choice == "R":
                if(Configurator.ConfirmQuestion()):
                    self.RemoveActiveEntity(entityConfig, ecm)
            elif choice == "e" or choice == "E":
                self.EditActiveEntity(entityConfig, ecm)

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
            i = 0
            for entity in entityList:
                print(i+1, "-", entity)
                i += 1

            print("\nQ - Come back")

            choice = input("\nSelect your choice: ")
            try:
                if choice == "q" or choice == "Q":
                    return
                else:
                    choice = int(choice)  # If not valid I have a ValueError
                    choice = choice - 1  # So now chosen entity = active entity in configurations
                    if choice >= 0 and choice < len(entityList):
                        # WIll also open the configuration menu
                        self.AddActiveEntity(entityList[choice], ecm)
                        choice = True
                    else:
                        raise ValueError()
            except ValueError:
                choice = False
                print("Please insert a valid choice")
            except Exception as e:
                choice = False
                self.Log(self.LOG_ERROR,
                         "Error in Entity select menu: " + str(e))

    def AddActiveEntity(self, entityName, ecm: EntityClassManager):
        """ From entity name, get its class and retrieve the configuration preset, then add to configuration dict """
        entityClass = ecm.GetClassFromName(entityName)
        try:
            preset = entityClass.ConfigurationPreset()

            if preset.HasQuestions():
                # Ask for Tag if the entity allows multi-instance - multi-instance has sense only if a preset is available
                if entityClass.AllowMultiInstance():
                    preset.AddTagQuestion()

                preset.PrintRules()
                preset.AskQuestions()

            else:
                print("No configuration needed for this Entity :)")

            self.EntityMenuPresetToConfiguration(entityName, preset)
        except Exception as e:
            print("Error during entity preset loading: " + str(e))

    def IsEntityActive(self, entityName) -> bool:
        """ Return True if an Entity is active """
        for entity in self.config[KEY_ACTIVE_ENTITIES]:
            if entityName == entity[KEY_ENTITY_TYPE]:
                return True
        return False

    def RemoveActiveEntity(self, entityConfig, ecm: EntityClassManager) -> None:
        """ Remove entity name from the list of active entities if present """
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
            preset = whClass.ConfigurationPreset()

            if preset.HasQuestions():
                preset.PrintRules()
                preset.AskQuestions()

            else:
                print("No configuration needed for this Warehouse :)")

            # Save added settings
            self.WarehouseMenuPresetToConfiguration(warehouseName, preset)
        except Exception as e:
            print("Error during warehouse preset loading: " + str(e))

    def EditActiveWarehouse(self, warehouseName, wcm: WarehouseClassManager) -> None:
        """ UI for single Warehouse settings edit """
        print("You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")
        # WarehouseMenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to read it later
        # TO implement only when I know how to add removable value while editing configurations
        pass  # TODO Implement

    def EditActiveEntity(self, entityConfig, ecm: WarehouseClassManager) -> None:
        """ UI for single Entity settings edit """
        print("You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")
        pass  # TODO Implement

    def RemoveActiveWarehouse(self, warehouseName) -> None:
        """ Remove warehouse name from the list of active warehouses if present """
        for wh in self.config[KEY_ACTIVE_WAREHOUSES]:
            if warehouseName == wh[KEY_WAREHOUSE_TYPE]:
                # I remove this wh from the list
                self.config[KEY_ACTIVE_WAREHOUSES].remove(wh)
                return

    def WarehouseMenuPresetToConfiguration(self, whName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict in warehouse part """
        _dict = preset.GetDict()
        _dict[KEY_WAREHOUSE_TYPE] = whName.replace("Warehouse", "")
        self.config[KEY_ACTIVE_WAREHOUSES].append(_dict)
        print("Configuration added for \""+whName+"\" :)")

    def EntityMenuPresetToConfiguration(self, entityName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict in entity part """
        _dict = preset.GetDict()
        _dict[KEY_ENTITY_TYPE] = entityName
        self.config[KEY_ACTIVE_ENTITIES].append(_dict)
        print("Configuration added for \""+entityName+"\" :)")

    def PrintSeparator(self):
        print("\n"+SEPARATOR_CHAR_NUMBER*'#')

    @staticmethod
    def ConfirmQuestion():
        value = input("You sure ? [y/n] ")
        if value == "y" or value == "Y":
            return True
        else:
            return False
