import os

from IoTuring.Logger.LogObject import LogObject
from IoTuring.Exceptions.Exceptions import UserCancelledException


from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager

from IoTuring.Configurator import ConfiguratorIO
from IoTuring.Configurator import messages

from InquirerPy import inquirer
from InquirerPy.separator import Separator


BLANK_CONFIGURATION = {'active_entities': [
    {"type": "AppInfo"}], 'active_warehouses': []}

KEY_ACTIVE_ENTITIES = "active_entities"
KEY_ACTIVE_WAREHOUSES = "active_warehouses"

KEY_WAREHOUSE_TYPE = "type"

KEY_ENTITY_TYPE = "type"
KEY_ENTITY_TAG = "tag"

CHOICE_GO_BACK = "< Go back"


class Configurator(LogObject):

    def __init__(self) -> None:
        # Clean the screen before first logs:
        self.pinned_message = False
        self.ClearScreen(pin_next_message=True)

        self.configuratorIO = ConfiguratorIO.ConfiguratorIO()
        self.config = self.LoadConfigurations()

    def GetConfigurations(self) -> dict:
        """ Return a copy of the configurations dict"""
        return self.config.copy()  # Safe return

    def Menu(self) -> None:
        """ UI for Entities and Warehouses settings """

        mainMenuChoices = [
            {"name": "Manage entities", "value": self.ManageEntities},
            {"name": "Manage warehouses", "value": self.ManageWarehouses},
            {"name": "Start IoTuring", "value": self.WriteConfigurations},
            {"name": "Help", "value": self.DisplayHelp},
            {"name": "Quit", "value": self.Quit},
        ]

        choice = self.DisplayMenu(
            choices=mainMenuChoices,
            message="IoTuring configurator",
            add_back_choice=False
        )
        choice()

    def ManageEntities(self) -> None:
        """ UI for Entities settings """
        ecm = EntityClassManager()

        manageEntitiesChoices = []

        for entityConfig in self.config[KEY_ACTIVE_ENTITIES]:
            manageEntitiesChoices.append(
                {"name": self.GetEntityLabel(entityConfig),
                 "value": entityConfig}
            )

            manageEntitiesChoices.sort(key=lambda d: d['name'])

        manageEntitiesChoices = [
            CHOICE_GO_BACK,
            {"name": "+ Add a new entity", "value": "AddNewEntity"},
            Separator()
        ] + manageEntitiesChoices

        choice = self.DisplayMenu(
            choices=manageEntitiesChoices,
            message="Manage entities",
            add_back_choice=False)

        if choice == "AddNewEntity":
            self.SelectNewEntity(ecm)
        elif choice == CHOICE_GO_BACK:
            self.Menu()
        else:
            self.ManageSingleEntity(choice, ecm)

    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = WarehouseClassManager()

        manageWhChoices = []

        availableWarehouses = wcm.ListAvailableClassesNames()
        for whName in availableWarehouses:
            short_wh_name = whName.replace("Warehouse", "")

            enabled_sign = " "
            if self.IsWarehouseActive(short_wh_name):
                enabled_sign = "X"

            manageWhChoices.append(
                {"name": f"[{enabled_sign}] - {short_wh_name}",
                 "value": short_wh_name})

        choice = self.DisplayMenu(
            choices=manageWhChoices,
            message="Select warehouse to manage (X for enabled)",
        )

        if choice == CHOICE_GO_BACK:
            self.Menu()
        else:
            self.ManageSingleWarehouse(choice, wcm)

    def DisplayHelp(self) -> None:
        self.DisplayMessage(messages.HELP_MESSAGE)
        self.Menu()

    def Quit(self) -> None:
        """ Save configurations and quit """
        self.WriteConfigurations()
        exit(0)

    def LoadConfigurations(self) -> dict:
        """ Reads the configuration file and returns configuration dictionary.
            If not available, returns the blank configuration """
        read_config = self.configuratorIO.readConfigurations()
        if read_config is None:
            read_config = BLANK_CONFIGURATION
        return read_config

    def WriteConfigurations(self) -> None:
        """ Save to configurations file """
        self.configuratorIO.writeConfigurations(self.config)

    def ManageSingleWarehouse(self, warehouseName, wcm: WarehouseClassManager):
        """UI for single Warehouse settings"""

        if self.IsWarehouseActive(warehouseName):
            manageWhChoices = [
                {"name": "Edit the warehouse settings", "value": "Edit"},
                {"name": "Remove the warehouse", "value": "Remove"}
            ]
        else:
            manageWhChoices = [
                {"name": "Add the warehouse", "value": "Add"}]

        choice = self.DisplayMenu(
            choices=manageWhChoices,
            message=f"Manage warehouse {warehouseName}"
        )

        if choice == CHOICE_GO_BACK:
            self.ManageWarehouses()
        elif choice == "Edit":
            self.EditActiveWarehouse(warehouseName, wcm)
        elif choice == "Add":
            self.AddActiveWarehouse(warehouseName, wcm)
        elif choice == "Remove":
            confirm = inquirer.confirm(message="Are you sure?").execute()

            if confirm:
                self.RemoveActiveWarehouse(warehouseName)
            else:
                self.ManageWarehouses()

    def ManageSingleEntity(self, entityConfig, ecm: EntityClassManager):
        """ UI to manage an active warehouse (edit config/remove) """

        manageEntityChoices = [
            {"name": "Edit the entity settings", "value": "Edit"},
            {"name": "Remove the entity", "value": "Remove"}
        ]

        choice = self.DisplayMenu(
            choices=manageEntityChoices,
            message=f"Manage entity {self.GetEntityLabel(entityConfig)}"
        )

        if choice == CHOICE_GO_BACK:
            self.ManageEntities()
        elif choice == "Edit":
            self.EditActiveEntity(entityConfig, ecm)  # type: ignore
        elif choice == "Remove":
            confirm = inquirer.confirm(message="Are you sure?").execute()

            if confirm:
                self.RemoveActiveEntity(entityConfig)
            else:
                self.ManageEntities()

    def SelectNewEntity(self, ecm: EntityClassManager):
        """ UI to add a new Entity """

        entityList = ecm.ListAvailableClassesNames()
        # Now I remove the entities that are active and that do not allow multi instances
        for activeEntity in self.config[KEY_ACTIVE_ENTITIES]:
            entityClass = ecm.GetClassFromName(
                activeEntity[KEY_ENTITY_TYPE])

            # Malformed entities, from different versions in config, just skip:
            if entityClass is None:
                continue

            # If the Allow Multi Instance option was changed:
            if activeEntity[KEY_ENTITY_TYPE] not in entityList:
                continue

            # not multi, remove:
            if not entityClass.AllowMultiInstance():  # type: ignore
                entityList.remove(activeEntity[KEY_ENTITY_TYPE])

        choice = self.DisplayMenu(
            choices=sorted(entityList),
            message="Available entities:",
            instruction="if you don't see the entity you want, it may be already active and may not accept another version of itself"

        )

        if choice == CHOICE_GO_BACK:
            self.ManageEntities()
        else:
            self.AddActiveEntity(choice, ecm)

    def AddActiveEntity(self, entityName, ecm: EntityClassManager):
        """ From entity name, get its class and retrieve the configuration preset, then add to configuration dict """
        entityClass = ecm.GetClassFromName(entityName)
        try:
            preset = entityClass.ConfigurationPreset()  # type: ignore

            if preset.HasQuestions():
                # Ask for Tag if the entity allows multi-instance - multi-instance has sense only if a preset is available
                if entityClass.AllowMultiInstance():  # type: ignore
                    preset.AddTagQuestion()

                self.DisplayMessage(messages.PRESET_RULES)
                self.DisplayMessage(f"Configure {entityName} Entity")
                preset.AskQuestions()

            else:
                self.DisplayMessage(
                    "No configuration needed for this Entity :)")

            self.EntityMenuPresetToConfiguration(entityName, preset)
        except UserCancelledException:
            self.DisplayMessage("Configuration cancelled", force_clear=True)

        except Exception as e:
            print("Error during entity preset loading: " + str(e))

        self.ManageEntities()

    def IsEntityActive(self, entityName) -> bool:
        """ Return True if an Entity is active """
        for entity in self.config[KEY_ACTIVE_ENTITIES]:
            if entityName == entity[KEY_ENTITY_TYPE]:
                return True
        return False

    def GetEntityLabel(self, entityConfig) -> str:
        """ Get the type name of entity, add tag if multi"""
        entityLabel = entityConfig[KEY_ENTITY_TYPE]
        if KEY_ENTITY_TAG in entityConfig:
            entityLabel += f" with tag {entityConfig[KEY_ENTITY_TAG]}"
        return entityLabel

    def RemoveActiveEntity(self, entityConfig) -> None:
        """ Remove entity name from the list of active entities if present """
        if entityConfig in self.config[KEY_ACTIVE_ENTITIES]:
            self.config[KEY_ACTIVE_ENTITIES].remove(entityConfig)

        self.DisplayMessage(
            f"Entity removed: {self.GetEntityLabel(entityConfig)}")
        self.ManageEntities()

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
            preset = whClass.ConfigurationPreset()  # type: ignore

            if preset.HasQuestions():
                self.DisplayMessage(messages.PRESET_RULES)
                preset.AskQuestions()

            else:
                self.DisplayMessage(
                    "No configuration needed for this Warehouse :)")

            # Save added settings
            self.WarehouseMenuPresetToConfiguration(warehouseName, preset)

        except UserCancelledException:
            self.DisplayMessage("Configuration cancelled", force_clear=True)

        except Exception as e:
            print("Error during warehouse preset loading: " + str(e))

        self.ManageWarehouses()

    def EditActiveWarehouse(self, warehouseName, wcm: WarehouseClassManager) -> None:
        """ UI for single Warehouse settings edit """
        self.DisplayMessage(
            "You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")

        self.ManageWarehouses()

        # TODO Implement
        # WarehouseMenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to read it later
        # TO implement only when I know how to add removable value while editing configurations

    def EditActiveEntity(self, entityConfig, ecm: WarehouseClassManager) -> None:
        """ UI for single Entity settings edit """
        self.DisplayMessage(
            "You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")

        self.ManageEntities()

        # TODO Implement

    def RemoveActiveWarehouse(self, warehouseName) -> None:
        """ Remove warehouse name from the list of active warehouses if present """
        for wh in self.config[KEY_ACTIVE_WAREHOUSES]:
            if warehouseName == wh[KEY_WAREHOUSE_TYPE]:
                # I remove this wh from the list
                self.config[KEY_ACTIVE_WAREHOUSES].remove(wh)

        self.DisplayMessage(f"Warehouse removed: {warehouseName}")
        self.ManageWarehouses()

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

    def ClearScreen(self, pin_next_message=False):
        """ Clear the screen on any platform. If self.pinned_message is True, it won't be cleared.

        Args:
            pin_next_message (bool, optional): Set self.pinned_message after clear. Defaults to False.
        """

        if not self.pinned_message:
            os.system("cls" if os.name == "nt" else "clear")

        if pin_next_message:
            self.pinned_message = True
        else:
            self.pinned_message = False

    def DisplayMenu(self, choices: list, message: str = "", add_back_choice=True, **kwargs):
        """ Wrapper for inquirer.select

        Args:
            choices (list): list of strings, dicts, see InquirerPy documentation
            message (str, optional): Title of the prompt. Defaults to "".
            add_back_choice (bool, optional): Add a go back option at the top. Defaults to True.

        Returns:
            The result of the prompt
        """

        if add_back_choice:
            choices = [CHOICE_GO_BACK,
                       Separator()
                       ] + choices

        if "max_height" not in kwargs:
            kwargs["max_height"] = "100%"

        self.ClearScreen()
        prompt = inquirer.select(
            message=message, choices=choices, **kwargs)

        if CHOICE_GO_BACK in choices:
            @prompt.register_kb("escape")
            def _handle_esc(event):
                prompt.content_control.selection["value"] = CHOICE_GO_BACK
                prompt._handle_enter(event)

        choice = prompt.execute()
        return choice

    def DisplayMessage(self, message: str, force_clear=False):
        """Display a message on the top of the screen, above menus

        Args:
            message (str): The message to display
            force_clear (bool): clear screen regardless previous
        """
        if force_clear:
            self.pinned_message = False
        self.ClearScreen(pin_next_message=True)
        print(message)
        print()
