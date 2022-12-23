import inspect  # To get this folder path and reach the configurations file
import os  # Configurations file path manipulation
import json

from simple_term_menu import TerminalMenu
from IoTuring.Logger.LogObject import LogObject
from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager
from IoTuring.Configurator.MenuPreset import MenuPreset

BLANK_CONFIGURATION = {'active_entities': [
    {"type": "AppInfo"}], 'active_warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"

KEY_WAREHOUSE_TYPE = "type"

KEY_ENTITY_TYPE = "type"
KEY_ENTITY_TAG = "tag"


class Configurator(LogObject):
    # Must be in the same folder of this file
    configurations_filename = "configurations.json"

    def __init__(self) -> None:
        self.config = None
        self.LoadConfigurations()

    def GetConfigurations(self):
        """ Return a copy of the configurations dict"""
        return self.config.copy()  # Safe return

    def Menu(self) -> None:
        """ UI for Entities and Warehouses settings """
        main_menu_options = ["Manage entities",
                             "Manage warehouses",
                             "Start IoTuring",
                             "Quit"]
        main_menu = TerminalMenu(
            menu_entries=main_menu_options,
            title="Configure IoTuring",
            clear_screen=True)
        main_menu_index = main_menu.show()
        if main_menu_index == 0:
            self.ManageEntities()
        elif main_menu_index == 1:
            self.ManageWarehouses()
        elif main_menu_index == 2:
            self.WriteConfigurations()
        elif main_menu_index == 3:
            self.WriteConfigurations()
            exit(0)

    def ManageEntities(self) -> None:
        """ UI for Entities settings """
        ecm = EntityClassManager()

        entity_menu_options = ["Go back",
                               "Add new entity",
                               ""]

        for entity in self.config[KEY_ACTIVE_ENTITIES]:
            if not KEY_ENTITY_TAG in entity:
                menu_text = entity[KEY_ENTITY_TYPE]
            else:
                menu_text = f"{entity[KEY_ENTITY_TYPE]} with tag {entity[KEY_ENTITY_TAG]}"
            entity_menu_options.append(menu_text)

        entity_menu = TerminalMenu(
            menu_entries=entity_menu_options,
            title="Active entities:",
            status_bar='Select entities to modify settings, select "Add new entity" to add new',
            skip_empty_entries=True)
        entity_menu_index = entity_menu.show()
        if entity_menu_index == 0:
            self.Menu()
        elif entity_menu_index == 1:
            self.SelectNewEntity(ecm)
        else:
            self.ManageSingleEntity(
                self.config[KEY_ACTIVE_ENTITIES][entity_menu_index - 3],
                ecm)

    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = WarehouseClassManager()
        availableWarehouses = wcm.ListAvailableClassesNames()

        wh_menu_options = ["Go back", ""]
        wh_shortnames = []

        for wh_name in availableWarehouses:
            wh_short_name = wh_name.replace("Warehouse", "")
            if not self.IsWarehouseActive(wh_short_name):
                active_sign = " "
            else:
                active_sign = "X"
            menu_text = f"({active_sign}) {wh_short_name}"
            wh_menu_options.append(menu_text)
            wh_shortnames.append(wh_short_name)

        wh_menu = TerminalMenu(
            menu_entries=wh_menu_options,
            title="Select warehouse",
            skip_empty_entries=True,
            status_bar="X means warehouse already enabled")
        wh_menu_index = wh_menu.show()
        if wh_menu_index == 0:
            self.Menu()
        else:
            wh_short_name = wh_shortnames[wh_menu_index - 2]
            self.ManageSingleWarehouse(wh_short_name, wcm)

    def LoadConfigurations(self) -> None:
        """ Load into a dict in self the configurations file in this script's folder """
        thisFolder = os.path.dirname(inspect.getfile(Configurator))
        path = os.path.join(thisFolder, self.configurations_filename)
        try:
            with open(path, "r") as f:
                self.config = json.loads(f.read())
        except:
            self.Log(self.LOG_WARNING, "It seems you haven't a configuration yet. Ensure you're using the configuration mode (-c) to enable your favourite entites and warehouses.")
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

        single_wh_menu_options = ["Go back", ""]

        if self.IsWarehouseActive(warehouseName):
            single_wh_menu_options.extend([
                'Edit warehouse settings',
                'Remove warehouse'
            ])
        else:
            single_wh_menu_options.append('Add warehouse')

        single_wh_menu = TerminalMenu(
            menu_entries=single_wh_menu_options,
            title=f"Manage {warehouseName}",
            skip_empty_entries=True)
        single_wh_menu_index = single_wh_menu.show()
        if single_wh_menu_index == 0:
            self.ManageWarehouses()
        if self.IsWarehouseActive(warehouseName):
            if single_wh_menu_index == 2:
                self.EditActiveWarehouse(warehouseName, wcm)
            elif single_wh_menu_index == 3:
                self.RemoveActiveWarehouse(warehouseName)
        else:
            self.AddActiveWarehouse(warehouseName, wcm)

    def ManageSingleEntity(self, entityConfig, ecm: EntityClassManager):
        """ UI to manage an active warehouse (edit config/remove) """
        single_entity_menu_options = [
            "Go back",
            "",
            "Edit entity settings",
            "Remove entity"]

        single_entity_menu = TerminalMenu(
            menu_entries=single_entity_menu_options,
            title=f"Manage {entityConfig[KEY_ENTITY_TYPE]}",
            skip_empty_entries=True)
        single_entity_menu_index = single_entity_menu.show()
        if single_entity_menu_index == 0:
            self.ManageEntities()
        elif single_entity_menu_index == 2:
            self.EditActiveEntity(entityConfig, ecm)
        elif single_entity_menu_index == 3:
            # get dependencies errors: if no one, okay; print those with error func otherwise.
            deps = self.CheckDependencies_AbleToRemove(
                entityConfig[KEY_ENTITY_TYPE], ecm)
            if not deps:
                del_menu_options = ["[Y] Yes", "[N] No"]
                del_menu = TerminalMenu(
                    menu_entries=del_menu_options,
                    title="Are you sure?")
                del_menu_index = del_menu.show()
                if del_menu_index == 0:
                    self.RemoveActiveEntity(entityConfig, ecm)
                    self.ManageEntities()
                else:
                    self.ManageSingleEntity(entityConfig=entityConfig, ecm=ecm)
            else:
                self.PrintDependencyError_RemoveEntity(deps)

    def SelectNewEntity(self, ecm: EntityClassManager):
        """ UI to add a new Entity """
        entityList = ecm.ListAvailableClassesNames()
        for activeEntity in self.config[KEY_ACTIVE_ENTITIES]:
            if not ecm.GetClassFromName(activeEntity[KEY_ENTITY_TYPE]).AllowMultiInstance():
                entityList.remove(activeEntity[KEY_ENTITY_TYPE])

        new_entity_menu_options = ["Go back", ""]

        new_entity_menu_options.extend(entityList)

        new_entity_menu = TerminalMenu(
            menu_entries=new_entity_menu_options,
            title="Available entities:",
            status_bar="if you don't see the entity you want, it may be already active and may not accept another version of itself",
            skip_empty_entries=True)
        new_entity_menu_index = new_entity_menu.show()
        if new_entity_menu_index == 0:
            self.ManageEntities()
        else:
            entity_nr = new_entity_menu_index - 2
            deps = self.CheckDependencies_AbleToActivate(
                entityList[entity_nr], ecm)
            if not deps:
                # WIll also open the configuration menu
                self.AddActiveEntity(entityList[entity_nr], ecm)
            else:
                self.PrintDependencyError_ActivateEntity(deps, ecm)

    def AddActiveEntity(self, entityName, ecm: EntityClassManager):
        """ From entity name, get its class and retrieve the configuration preset, then add to configuration dict """
        entityClass = ecm.GetClassFromName(entityName)
        try:
            preset = entityClass.ConfigurationPreset()

            if preset is not None:  # Then let's configure the Entity
                # Ask also for Tag if the entity allows multi-instance
                if entityClass.AllowMultiInstance():
                    preset.AddTagQuestion()

                preset.PrintRules()
                for index, question in enumerate(preset.ListEntries()):
                    preset.Question(index)

            else:
                preset = MenuPreset()  # Use blank
                self.Log(self.LOG_INFO,
                         "No configuration needed for this Entity :)")

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
        # TODO Check if no dependencies from it

        for activeEntity in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
            if activeEntity != entityConfig:
                # Get class from entity type
                entityClass = ecm.GetClassFromName(
                    activeEntity[KEY_ENTITY_TYPE])
                # Retrieve entity dependencies
                deps = entityClass.GetDependenciesList()
                # Check if entity I want to remove is dependent from the entity I'm iterating
                if entityConfig[KEY_ENTITY_TYPE] in deps:
                    raise Exception("Can't remove this entity because " +
                                    activeEntity[KEY_ENTITY_TYPE] + " depends from it :(")

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
            # With the use of "type" I get the staticmethod of the subclass and not of the parentclass
            preset = whClass.ConfigurationPreset()

            if preset is not None:
                preset.PrintRules()

                for index, question in enumerate(preset.ListEntries()):
                    preset.Question(index)
            else:
                preset = MenuPreset()  # Use blank
                print("No configuration needed for this Warehouse :)")

            # Save added settings
            self.WarehouseMenuPresetToConfiguration(warehouseName, preset)
        except Exception as e:
            print("Error during warehouse preset loading: " + str(e))

    def NotImplementedMessage(self, previous_menu=None, *args, **kwargs):
        """Print a message about a not implemented function, with an OK button. """
        title = "This function is not implemented yet, change the configuration file manually. Sorry for the inconvenience"
        if self.OkMenu(title):
            if not previous_menu:
                self.Menu()
            else:
                previous_menu(*args, **kwargs)

    def EditActiveWarehouse(self, warehouseName, wcm: WarehouseClassManager) -> None:
        """ UI for single Warehouse settings edit """
        # WarehouseMenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to read it later
        # TO implement only when I know how to add removable value while editing configurations
        # TODO Implement
        self.NotImplementedMessage(
            self.ManageSingleWarehouse, warehouseName=warehouseName, wcm=wcm)

    def EditActiveEntity(self, entityConfig, ecm: EntityClassManager) -> None:
        """ UI for single Entity settings edit """
        # TODO Implement
        self.NotImplementedMessage(
            self.ManageSingleEntity, entityConfig=entityConfig, ecm=ecm)

    def RemoveActiveWarehouse(self, warehouseName) -> None:
        """ Remove warehouse name from the list of active warehouses if present """
        for wh in self.config[KEY_ACTIVE_WAREHOUSES]:
            if warehouseName == wh[KEY_WAREHOUSE_TYPE]:
                # I remove this wh from the list
                self.config[KEY_ACTIVE_WAREHOUSES].remove(wh)
        self.ManageWarehouses()

    def WarehouseMenuPresetToConfiguration(self, whName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict in warehouse part """
        _dict = preset.GetDict()
        _dict[KEY_WAREHOUSE_TYPE] = whName.replace("Warehouse", "")
        self.config[KEY_ACTIVE_WAREHOUSES].append(_dict)
        if self.OkMenu(f'Configuration added for "{whName}" :)'):
            self.ManageWarehouses()

    def EntityMenuPresetToConfiguration(self, entityName, preset) -> None:
        """ Get a MenuPreset with responses and add the entries to the configurations dict in entity part """
        _dict = preset.GetDict()
        _dict[KEY_ENTITY_TYPE] = entityName
        self.config[KEY_ACTIVE_ENTITIES].append(_dict)
        if self.OkMenu(f'Configuration added for "{entityName}" :)'):
            self.ManageEntities()

    def CheckDependencies_AbleToActivate(self, entityToActivate, entityClassManager: EntityClassManager):
        """ Return list of entities depends on. """
        entityClass = entityClassManager.GetClassFromName(entityToActivate)
        dependingOn = entityClass.GetDependenciesList()
        for dependency in entityClass.GetDependenciesList():
            for active_entity in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
                if dependency == active_entity[KEY_ENTITY_TYPE]:
                    dependingOn.remove(dependency)
        return dependingOn

    def CheckDependencies_AbleToRemove(self, entityToDisable, entityClassManager: EntityClassManager):
        """ Return list of entities depend on this. """
        # Each entity has a dependency list. Check if active entities do not rely on this.
        dependingOnThis = []
        for activeEntity in self.GetConfigurations()[KEY_ACTIVE_ENTITIES]:
            # List of dependencies is in the class: load the class
            entityClass = entityClassManager.GetClassFromName(
                activeEntity[KEY_ENTITY_TYPE])
            for dependency in entityClass.GetDependenciesList():
                if dependency == entityToDisable:
                    dependingOnThis.append(activeEntity[KEY_ENTITY_TYPE])
        return dependingOnThis

    def PrintDependencyError_ActivateEntity(self, dependenci, ecm: EntityClassManager):
        """ Prints a message with the dependencies the user has to activate before activating this entity """

        dependency_message = [
            "!!! You can't activate this Entity. Please activate the following entities in order to use this one: !!!"]

        for dependency in dependencies:
            dependency_message.append("---> " + dependency + " <----")
        dependency_message.append("End of dependencies list")
        if self.OkMenu(dependency_message):
            self.SelectNewEntity(ecm=ecm)

    def PrintDependencyError_RemoveEntity(self, dependencies):
        """ Prints a message with the dependencies the user has to remove before removing this entity """

        dependency_message = [
            "!!! You can't remove this Entity. Please remove the following entities in order to remove this one: !!!"]

        for dependency in dependencies:
            dependency_message.append("---> " + dependency + " <----")

        dependency_message.append("End of dependencies list")
        if self.OkMenu(dependency_message):
            self.ManageEntities()

    def OkMenu(self, title):
        """ Display a small dialog with an OK button"""
        ok_menu = TerminalMenu(
            menu_entries=["OK"],
            title=title)
        ok_menu_index = ok_menu.show()
        if ok_menu_index == 0:
            return True
