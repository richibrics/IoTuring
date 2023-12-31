import os
import subprocess
import shutil

from IoTuring.Configurator.MenuPreset import QuestionPreset
from IoTuring.Configurator.Configuration import FullConfiguration, SingleConfiguration, KEY_ACTIVE_ENTITIES, KEY_ACTIVE_WAREHOUSES

from IoTuring.Logger.LogObject import LogObject
from IoTuring.Exceptions.Exceptions import UserCancelledException

from IoTuring.ClassManager.EntityClassManager import EntityClassManager
from IoTuring.ClassManager.WarehouseClassManager import WarehouseClassManager

from IoTuring.Configurator import ConfiguratorIO
from IoTuring.Configurator import messages

from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.AppSettings import AppSettings

from InquirerPy import inquirer
from InquirerPy.separator import Separator


CHOICE_GO_BACK = "< Go back"


class Configurator(LogObject):

    def __init__(self) -> None:

        self.pinned_lines = 1

        self.configuratorIO = ConfiguratorIO.ConfiguratorIO()

        # Load configuration from file, create Configuration object:
        config_dict_from_file = self.configuratorIO.readConfigurations()
        if config_dict_from_file:
            self.config = FullConfiguration(config_dict_from_file)
        else:
            # Create blank config:
            self.config = FullConfiguration()

    def CheckFile(self) -> None:
        """ Make sure config file exists or can be created """
        if not self.configuratorIO.checkConfigurationFileExists():
            if self.configuratorIO.shouldMoveOldConfig():

                moveFile = inquirer.confirm(
                    message=" ".join([
                        "A configuration file was found in the old location.",
                        "Do you want to move it to the new location?",
                        "If not, a new blank configuration will be used."]),
                    default=True
                ).execute()

                self.configuratorIO.manageOldConfig(moveFile)

                # Reload config if it was moved:
                if moveFile:
                    self.__init__()

    def OpenConfigInEditor(self):
        """ Open configuration file in an editor """
        if not self.configuratorIO.checkConfigurationFileExists():
            self.Log(self.LOG_ERROR,
                     "Configuration file not found, run with -c to create one!")
        else:
            config_path = str(self.configuratorIO.getFilePath())
            self.Log(self.LOG_INFO, f"Opening file: \"{config_path}\"")

            if OsD.IsWindows():
                os.startfile(config_path)  # type: ignore
                return
            else:
                editors = [
                    OsD.GetEnv("EDITOR"),
                    "nano",
                    "vim"
                ]
                editor_command = next(
                    (e for e in editors if OsD.CommandExists(e)), "")
                if editor_command:
                    subprocess.run(f'{editor_command} "{config_path}"',
                                   shell=True, close_fds=True)
                    return

            self.Log(self.LOG_WARNING, "No editor found")

    def Menu(self) -> None:
        """ UI for Entities and Warehouses settings """

        mainMenuChoices = [
            {"name": "Manage entities", "value": self.ManageEntities},
            {"name": "Manage warehouses", "value": self.ManageWarehouses},
            {"name": "App Settings", "value": self.ManageSettings},
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

        for entityConfig in self.config.GetConfigsInCategory(KEY_ACTIVE_ENTITIES):
            manageEntitiesChoices.append(
                {"name": entityConfig.GetLabel(),
                 "value": entityConfig}
            )

        manageEntitiesChoices.sort(key=lambda d: d['name'])

        manageEntitiesChoices = [
            CHOICE_GO_BACK,
            {"name": "+ Add a new entity", "value": "AddNewEntity"},
            {"name": "? Unsupported entities", "value": "UnsupportedEntities"},
            Separator()
        ] + manageEntitiesChoices

        choice = self.DisplayMenu(
            choices=manageEntitiesChoices,
            message="Manage entities",
            add_back_choice=False)

        if choice == "AddNewEntity":
            self.SelectNewEntity(ecm)
        elif choice == "UnsupportedEntities":
            self.ShowUnsupportedEntities(ecm)
        elif choice == CHOICE_GO_BACK:
            self.Menu()
        else:
            self.ManageSingleEntity(choice)

    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = WarehouseClassManager()

        manageWhChoices = []

        availableWarehouses = wcm.ListAvailableClasses()
        for whClass in availableWarehouses:

            enabled_sign = " "
            if self.IsWarehouseActive(whClass):
                enabled_sign = "X"

            manageWhChoices.append(
                {"name": f"[{enabled_sign}] - {whClass.NAME}",
                 "value": whClass})

        choice = self.DisplayMenu(
            choices=manageWhChoices,
            message="Select warehouse to manage (X for enabled)",
        )

        if choice == CHOICE_GO_BACK:
            self.Menu()
        else:
            self.ManageSingleWarehouse(choice)

    def ManageSettings(self):
        preset = AppSettings.ConfigurationPreset()

        settingsChoices = []

        for entry in preset.presets:
            # Load config instead of default:
            if self.config.GetAppSettings().HasConfigKey(entry.key):
                value = self.config.GetAppSettings().GetConfigValue(entry.key)
            else:
                value = entry.default

            settingsChoices.append({
                "name": f"{entry.name}: {value}",
                "value": entry.key
            })

        choice = self.DisplayMenu(
            choices=settingsChoices,
            message="Select setting to edit")

        if choice == CHOICE_GO_BACK:
            self.Menu()
        else:
            q_preset = preset.GetPresetByKey(choice)
            if q_preset:
                self.ManageSingleSetting(q_preset)
            else:
                self.DisplayMessage(f"Question preset not found: {choice}")
                self.ManageSettings()

    def ManageSingleSetting(self, q_preset: QuestionPreset):

        appSettingsConfig = self.config.GetAppSettings()

        # Load config as default:
        if appSettingsConfig.HasConfigKey(q_preset.key):
            q_preset.default = appSettingsConfig.GetConfigValue(q_preset.key)

        value = q_preset.Ask()

        if value:
            # Add to config:
            appSettingsConfig.UpdateConfigValue(q_preset.key, value)

        self.ManageSettings()

    def DisplayHelp(self) -> None:
        self.DisplayMessage(messages.HELP_MESSAGE)
        # Help message is too long:
        self.pinned_lines = 1
        self.Menu()

    def Quit(self) -> None:
        """ Save configurations and quit """
        self.WriteConfigurations()
        exit(0)

    def WriteConfigurations(self) -> None:
        """ Save to configurations file """
        self.configuratorIO.writeConfigurations(self.config.ToDict())
        # Reload AppSettings
        AppSettings().LoadConfiguration(self)

    def ManageSingleWarehouse(self, whClass):
        """UI for single Warehouse settings"""

        if self.IsWarehouseActive(whClass):
            manageWhChoices = [
                {"name": "Edit the warehouse settings", "value": "Edit"},
                {"name": "Remove the warehouse", "value": "Remove"}
            ]
        else:
            manageWhChoices = [
                {"name": "Add the warehouse", "value": "Add"}]

        choice = self.DisplayMenu(
            choices=manageWhChoices,
            message=f"Manage warehouse {whClass.NAME}"
        )

        if choice == CHOICE_GO_BACK:
            self.ManageWarehouses()
        elif choice == "Add":
            self.AddActiveClass(whClass, KEY_ACTIVE_WAREHOUSES)
            self.ManageWarehouses()
        else:
            whConfig = self.config.GetConfigsOfType(whClass.NAME)[0]
            if choice == "Edit":
                self.EditActiveWarehouse(whConfig)
            elif choice == "Remove":
                confirm = inquirer.confirm(message="Are you sure?").execute()

                if confirm:
                    self.RemoveActiveConfiguration(whConfig)

                self.ManageWarehouses()

    def ManageSingleEntity(self, entityConfig: SingleConfiguration):
        """ UI to manage an active entity (edit config/remove) """

        manageEntityChoices = [
            {"name": "Edit the entity settings", "value": "Edit"},
            {"name": "Remove the entity", "value": "Remove"}
        ]

        choice = self.DisplayMenu(
            choices=manageEntityChoices,
            message=f"Manage entity {entityConfig.GetLabel()}"
        )

        if choice == CHOICE_GO_BACK:
            self.ManageEntities()
        elif choice == "Edit":
            self.EditActiveEntity(entityConfig)  # type: ignore
        elif choice == "Remove":
            confirm = inquirer.confirm(message="Are you sure?").execute()

            if confirm:
                self.RemoveActiveConfiguration(entityConfig)

            self.ManageEntities()

    def SelectNewEntity(self, ecm: EntityClassManager):
        """ UI to add a new Entity """

        # entity classes without unsupported entities:
        entityClasses = [
            e for e in ecm.ListAvailableClasses() if e.SystemSupported()]

        entityChoices = []

        for entityClass in entityClasses:
            if self.config.GetConfigsOfType(entityClass.NAME):
                if not entityClass.AllowMultiInstance():
                    continue
            entityChoices.append(
                {"name": entityClass.NAME, "value": entityClass}
            )

        entityChoices.sort(key=lambda d: d['name'])

        choice = self.DisplayMenu(
            choices=entityChoices,
            message="Available entities:",
            instruction="if you don't see the entity, it may be already active and not accept another activation, or not supported by your system"
        )

        if choice == CHOICE_GO_BACK:
            self.ManageEntities()
        else:
            self.AddActiveClass(choice, KEY_ACTIVE_ENTITIES)
            self.ManageEntities()

    def ShowUnsupportedEntities(self, ecm: EntityClassManager):
        """ UI to show unsupported entities """

        # entity classnames without unsupported entities:
        unsupportedEntityList = []
        for eClass in ecm.ListAvailableClasses():
            try:
                eClass.CheckSystemSupport()
            except Exception as e:
                unsupportedEntityList.append(f"\t{eClass.NAME}: {str(e)}")

        if not unsupportedEntityList:
            self.DisplayMessage("No unsupported entities :)")

        else:
            msg = "\n".join(sorted(unsupportedEntityList))
            self.DisplayMessage("Unsupported entities:\n" + msg)

        self.ManageEntities()

    def RemoveActiveConfiguration(self, singleConfig: SingleConfiguration) -> None:
        """ Remove configuration (wh or entity) """
        self.config.RemoveActiveConfiguration(singleConfig)
        self.DisplayMessage(
            f"{singleConfig.GetCategoryName()} removed: {singleConfig.GetLabel()}")

    def IsWarehouseActive(self, whClass) -> bool:
        """ Return True if a warehouse is active """
        return bool(self.config.GetConfigsOfType(whClass.NAME))

    def AddActiveClass(self, ioClass, config_category: str) -> None:
        try:
            preset = ioClass.ConfigurationPreset()

            if preset.HasQuestions():

                if config_category == KEY_ACTIVE_ENTITIES:
                    # Ask for Tag if the entity allows multi-instance - multi-instance has sense only if a preset is available
                    if ioClass.AllowMultiInstance():
                        preset.AddTagQuestion()

                self.DisplayMessage(messages.PRESET_RULES)
                self.DisplayMessage(
                    f"Configure {ioClass.NAME} {ioClass.CATEGORY_NAME}")
                preset.AskQuestions()
                self.ClearScreen(force_clear=True)

            else:
                self.DisplayMessage(
                    f"No configuration needed for this {ioClass.CATEGORY_NAME} :)")

            self.config.AddConfiguration(
                config_category, preset.GetDict(), ioClass.NAME)

        except UserCancelledException:
            self.DisplayMessage("Configuration cancelled", force_clear=True)

        except Exception as e:
            print(
                f"Error during {ioClass.CATEGORY_NAME} preset loading: {str(e)}")

    def EditActiveWarehouse(self, whConfig: SingleConfiguration) -> None:
        """ UI for single Warehouse settings edit """
        self.DisplayMessage(
            "You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")

        self.ManageWarehouses()

        # TODO Implement
        # WarehouseMenuPresetToConfiguration appends a warehosue to the conf so here I should remove it to read it later
        # TO implement only when I know how to add removable value while editing configurations

    def EditActiveEntity(self, entityConfig: SingleConfiguration) -> None:
        """ UI for single Entity settings edit """
        self.DisplayMessage(
            "You can't do that at the moment, change the configuration file manually. Sorry for the inconvenience")

        self.ManageEntities()

        # TODO Implement

    def ClearScreen(self, force_clear=False):
        """ Clear the screen on any platform. If self.pinned_lines greater than zero, it won't be cleared.

        Args:
            force_clear (bool, optional): Clear even pinned messages. Defaults to False.
        """

        if self.pinned_lines == 0 or force_clear:
            self.ClearTerminal()
            self.pinned_lines = 0

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

            # Default max_height:
            kwargs["max_height"] = "100%"

            # Actual lines in the terminal. fallback to 0 on error:
            terminal_lines = shutil.get_terminal_size(fallback=(0, 0)).lines

            # Check for pinned messages:
            if terminal_lines > 0 and self.pinned_lines > 0:

                # Lines of message and instruction if too long:
                if "instruction" in kwargs:
                    message_lines = ((len(kwargs["instruction"]) + len(message) + 3)
                                     / shutil.get_terminal_size().columns) // 1
                # Add only the line of the message:
                else:
                    message_lines = 1

                # Calculate nr of lines required to display:
                required_lines = len(choices) + \
                    self.pinned_lines + message_lines

                # Set the calculated height:
                if required_lines > terminal_lines:
                    kwargs["max_height"] = terminal_lines \
                        - self.pinned_lines - message_lines

        self.ClearScreen()
        # Reset pinned lines:
        self.pinned_lines = 0

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

        self.ClearScreen(force_clear)
        self.pinned_lines += message.count('\n') + 2
        print(message)
        print()

    @staticmethod
    def ClearTerminal():
        """Clear the terminal screen on any platform"""
        os.system("cls" if os.name == "nt" else "clear")
