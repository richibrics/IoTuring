import inspect  # To get this folder path and reach the configurations file
import os  # Configurations file path manipulation
import json

from ClassManager.EntityClassManager import EntityClassManager
from ClassManager.WarehouseClassManager import WarehouseClassManager

BLANK_CONFIGURATION = {'active_entities': [], 'warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"

KEY_WAREHOUSE_TYPE = "type"

class Configurator:
    # Must be in the same folder of this file
    configurations_filename = "configurations.json"

    def __init__(self) -> None:
        self.config = None
        self.LoadConfigurations()

    def GetConfigurations(self):
        return self.config.copy() # Safe return

    def Menu(self) -> None:
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
                    self.WriteConfigurations()
                elif choice == "q" or choice == "Q":
                    self.WriteConfigurations()
                    exit(0)
                else:
                    print("Invalid choice")
                    choice = False

    def SelectEntities(self) -> None:
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
                                # Enable it (add to active entities list)
                                self.AddActiveEntity(availableEntities[choice])
                            choice = True
                        else:
                            raise Exception("Choice out of entities range")
                    except:
                        choice = False


    def ManageWarehouses(self) -> None:
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
                            print("Invalid choice")
                            raise Exception("Choice out of warehouses range")
                    except Exception as e:
                        print("Error in warehouses menu:",str(e))
                        choice = False

    def LoadConfigurations(self) -> None:
        thisFolder = os.path.dirname(inspect.getfile(Configurator))
        path = os.path.join(thisFolder, self.configurations_filename)
        try:
            with open(path, "r") as f:
                self.config = json.loads(f.read())
        except:
            self.config = BLANK_CONFIGURATION

    def WriteConfigurations(self) -> None:
        thisFolder = os.path.dirname(inspect.getfile(Configurator))
        path = os.path.join(thisFolder, self.configurations_filename)
        with open(path, "w") as f:
            f.write(json.dumps(self.config))

    def ManageSingleWarehouse(self, warehouseName, wcm: WarehouseClassManager):
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
        return entityName in self.config[KEY_ACTIVE_ENTITIES]

    def AddActiveEntity(self, entityName) -> None:
        if not entityName in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].append(entityName)
   
    def RemoveActiveEntity(self, entityName) -> None:
        if entityName in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].remove(entityName)

    def IsWarehouseActive(self, warehouseName) -> bool:
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
        print("You can't do that at the moment bro")
        # MenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to readd it later
        # TO implement only when I know how to add removable value while editing configurations
        pass # TODO Implement
   
    def RemoveActiveWarehouse(self, warehouseName) -> None:
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



class MenuPreset():

    def __init__(self) -> None:
        self.preset = []

    def AddEntry(self,name,key,default=None,mandatory=False):
        self.preset.append({"name":name,"key":key,"default":default,"mandatory":mandatory,"value": None})

    def ListEntries(self):
        return self.preset

    def Question(self,id):
        try:
            question = ""
            if id<len(self.preset):
                question = "Add value for \""+self.preset[id]["name"]+"\""
                if self.preset[id]['mandatory']:
                    question = question + " {!}"
                if self.preset[id]["default"] is not None:
                    question = question + " [" + str(self.preset[id]["default"])+"]"

                question = question + ": "
                
                value = input(question)

                while value == "" and self.preset[id]["mandatory"]: # Mandatory loop
                    value = input("You must provide a value for this key: ")

                if value == "":
                    if self.preset[id]["default"] is not None:
                        self.preset[id]['value'] = self.preset[id]["default"] # Set in the preset
                        return self.preset[id]["default"] # Also return it
                    else:
                        self.preset[id]['value'] = None # Set in the preset
                        return None # Also return it
                else:
                    self.preset[id]['value'] = value # Set in the preset
                    return value # Also return it
        except Exception as e:
            print("Error while making the question:",e)
    
    def GetDict(self) -> dict:
        """ Get a dict with keys and responses"""
        result = {}
        for entry in self.preset:
            result[entry['key']]=entry['value']
        return result
                
class ConfiguratorLoader():
    configurator = None
    def __init__(self,configurator: Configurator) -> None:
        self.configurations = configurator.GetConfigurations()

    def LoadWarehouses(self) -> list: # Return list of instances initialized using their configurations
        warehouses = []
        wcm = WarehouseClassManager()
        for activeWarehouse in self.configurations[KEY_ACTIVE_WAREHOUSES]:
            # Get WareHouse named like in config type field, then init it with configs and add it to warehouses list
            warehouses.append(wcm.GetClassFromName(activeWarehouse[KEY_WAREHOUSE_TYPE]+"Warehouse").InstantiateWithConfiguration(activeWarehouse))
        return warehouses

    # warehouses[0].AddEntity(eM.NewEntity(eM.EntityNameToClass("Username")).getInstance()): may be useful
    def LoadEntities(self) -> list: # Return list of entities initialized
        pass
        # TODO IMPLEMENT

