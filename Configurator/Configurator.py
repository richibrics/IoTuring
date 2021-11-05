import inspect  # To get this folder path and reach the configurations file
import os  # Configurations file path manipulation
import json

from ClassManager.EntityClassManager import EntityClassManager

BLANK_CONFIGURATION = {'active_entities': [], 'warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"


class Configurator:
    # Must be in the same folder of this file
    configurations_filename = "configurations.json"

    def __init__(self) -> None:
        self.config = None
        self.LoadConfigurations()

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
        cm = EntityClassManager()
        while(True):
            print("\nSelect your entities (X for enabled):")
            availableEntities = cm.ListAvailableClassesNames()
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
        # TODO Implement
        pass

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

    def IsEntityActive(self, entityName) -> bool:
        return entityName in self.config[KEY_ACTIVE_ENTITIES]

    def AddActiveEntity(self, entityName) -> None:
        if not entityName in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].append(entityName)
   
    def RemoveActiveEntity(self, entityName) -> None:
        if entityName in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].remove(entityName)
