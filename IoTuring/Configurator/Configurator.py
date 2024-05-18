import os
import subprocess
import sys

from IoTuring.Configurator.MenuPreset import QuestionPreset
from IoTuring.Configurator.Configuration import FullConfiguration, SingleConfiguration
from IoTuring.Configurator import ConfiguratorIO
from IoTuring.Configurator import messages

from IoTuring.ClassManager.ClassManager import ClassManager, KEY_ENTITY, KEY_WAREHOUSE, KEY_SETTINGS

from IoTuring.Logger.LogObject import LogObject
from IoTuring.Exceptions.Exceptions import UserCancelledException
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.MyApp.SystemConsts import TerminalDetection

from InquirerPy import inquirer
from InquirerPy.separator import Separator


CHOICE_GO_BACK = "< Go back"


class Configurator(LogObject):

    def __init__(self) -> None:

        self.pinned_lines = 1

        # Load configuration from file:
        self.configuratorIO = ConfiguratorIO.ConfiguratorIO()
        config_dict_from_file = self.configuratorIO.readConfigurations()

        # Create FullConfiguration object:
        self.config = FullConfiguration(config_dict_from_file)

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
            {"name": "Settings", "value": self.ManageSettings},
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
        ecm = ClassManager(KEY_ENTITY)

        manageEntitiesChoices = []

        for entityConfig in self.config.GetConfigsOfClass(KEY_ENTITY):
            manageEntitiesChoices.append(
                {"name": entityConfig.GetLabel(),
                 "value": entityConfig}
            )

        manageEntitiesChoices.sort(key=lambda d: d['name'])

        manageEntitiesChoices = [
            CHOICE_GO_BACK,
            {"name": "+ Add a new entity", "value": "SelectNewEntity"},
            {"name": "? Unsupported entities", "value": "UnsupportedEntities"},
            Separator()
        ] + manageEntitiesChoices

        choice = self.DisplayMenu(
            choices=manageEntitiesChoices,
            message="Manage entities",
            add_back_choice=False)

        if choice == "SelectNewEntity":
            self.SelectNewEntity(ecm)
        elif choice == "UnsupportedEntities":
            self.ShowUnsupportedEntities(ecm)
        elif choice == CHOICE_GO_BACK:
            self.Menu()
        else:
            entityClass = ecm.GetClassFromName(choice.GetType())
            self.ManageActiveConfiguration(entityClass, choice)
            self.ManageEntities()

    def ManageWarehouses(self) -> None:
        """ UI for Warehouses settings """
        wcm = ClassManager(KEY_WAREHOUSE)

        manageWhChoices = []

        availableWarehouses = wcm.ListAvailableClasses()
        for whClass in availableWarehouses:

            enabled_sign = "X" if self.IsClassActive(whClass) else " "

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
            if self.IsClassActive(choice):
                whConfig = self.config.GetConfigsOfType(choice.NAME)[0]
                self.ManageActiveConfiguration(choice, whConfig)
                self.ManageWarehouses()
            else:
                self.AddNewWarehouse(choice)

    def ManageSettings(self) -> None:
        """ UI for App and other Settings """

        scm = ClassManager(KEY_SETTINGS)

        choices = [
            CHOICE_GO_BACK,
            {"name": "x Reset all settings to default", "value": "ResetSettings"},
            Separator()
        ]

        availableSettings = scm.ListAvailableClasses()
        for sClass in availableSettings:

            choices.append(
                {"name": sClass.NAME + " Settings",
                 "value": sClass})

        choice = self.DisplayMenu(
            choices=choices,
            message=f"Select settings to edit",
            add_back_choice=False
        )

        if choice == CHOICE_GO_BACK:
            self.Menu()
        elif choice == "ResetSettings":

            confirm = inquirer.confirm(message="Are you sure?").execute()
            if confirm:
                settings_configs = self.config.GetConfigsOfClass(KEY_SETTINGS)
                if settings_configs:
                    for s in settings_configs:
                        self.config.RemoveActiveConfiguration(s)

                self.DisplayMessage("All settings were reset to default")

            self.ManageSettings()

        else:
            if not self.IsClassActive(choice):
                self.config.configs.append(choice.GetDefaultConfigurations())

            settings_config = self.config.GetConfigsOfType(choice.NAME)[0]

            self.EditActiveConfiguration(
                choice, settings_config)

            self.ManageSettings()

    def IsClassActive(self, typeClass) -> bool:
        """Check if class has an active configuration """
        return bool(self.config.GetConfigsOfType(typeClass.NAME))

    def DisplayHelp(self) -> None:
        """" Display the help message, and load the main menu """
        self.DisplayMessage(messages.HELP_MESSAGE)
        # Help message is too long:
        self.pinned_lines = 1
        self.Menu()

    def Quit(self) -> None:
        """ Save configurations and quit """
        self.WriteConfigurations()
        sys.exit(0)

    def WriteConfigurations(self) -> None:
        """ Save to configurations file """
        self.configuratorIO.writeConfigurations(self.config.ToDict())

    def AddNewWarehouse(self, whClass) -> None:
        """UI to add a new warehouse"""

        choices = [
            {"name": "Add the warehouse", "value": "Add"}]

        choice = self.DisplayMenu(
            choices=choices,
            message=f"Manage warehouse {whClass.NAME}"
        )

        if choice == CHOICE_GO_BACK:
            self.ManageWarehouses()
        elif choice == "Add":
            self.AddNewConfiguration(whClass)
            self.ManageWarehouses()

    def ManageActiveConfiguration(self, typeClass, single_config: SingleConfiguration) -> None:
        choices = [
            {"name": f"Edit the {typeClass.GetClassKey()} settings",
             "value": "Edit"},
            {"name": f"Remove the {typeClass.GetClassKey()}", "value": "Remove"}
        ]

        choice = self.DisplayMenu(
            choices=choices,
            message=f"Manage {typeClass.GetClassKey()} {typeClass.NAME}"
        )

        if choice == CHOICE_GO_BACK:
            return
        elif choice == "Edit":
            self.EditActiveConfiguration(
                typeClass, single_config)
            self.ManageActiveConfiguration(typeClass, single_config)

        elif choice == "Remove":
            self.RemoveActiveConfiguration(single_config)

    def SelectNewEntity(self, ecm: ClassManager):
        """ UI to select new Entity to add """

        # entity classes without unsupported entities:
        entityClasses = [
            e for e in ecm.ListAvailableClasses() if e.SystemSupported()]

        entityChoices = []

        for entityClass in entityClasses:

            # If already added append only if multi allowed:
            if self.IsClassActive(entityClass):
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
            self.AddNewConfiguration(choice)
            self.ManageEntities()

    def ShowUnsupportedEntities(self, ecm: ClassManager):
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
        confirm = inquirer.confirm(message="Are you sure?").execute()
        if confirm:
            self.config.RemoveActiveConfiguration(singleConfig)
            self.DisplayMessage(
                f"{singleConfig.GetClassKey().capitalize()} removed: {singleConfig.GetLabel()}")

    def AddNewConfiguration(self, typeClass) -> None:
        """Add a wh or Entity to configuration. 

        Args:
            typeClass: the WH or Entity class to add
        """
        try:
            preset = typeClass.ConfigurationPreset()

            if preset.HasQuestions():

                if typeClass.AllowMultiInstance():
                    preset.AddTagQuestion()

                self.DisplayMessage(messages.PRESET_RULES)
                self.DisplayMessage(
                    f"Configure {typeClass.NAME} {typeClass.GetClassKey()}")
                preset.AskQuestions()
                self.ClearScreen(force_clear=True)

            else:
                self.DisplayMessage(
                    f"No configuration needed for this {typeClass.GetClassKey()} :)")

            self.config.AddConfiguration(
                typeClass.GetClassKey(), typeClass.NAME, preset.GetDict())

        except UserCancelledException:
            self.DisplayMessage("Configuration cancelled", force_clear=True)

        except Exception as e:
            print(
                f"Error during {typeClass.GetClassKey()} preset loading: {str(e)}")

    def EditActiveConfiguration(self, typeClass, single_config: SingleConfiguration) -> None:
        """ UI for changing settings """
        preset = typeClass.ConfigurationPreset()

        if preset.HasQuestions():

            choices = []

            # Add tag:
            if typeClass.AllowMultiInstance():
                preset.AddTagQuestion()

            for entry in preset.presets:
                if entry.ShouldDisplay(single_config.ToDict(include_type=False)):

                    # Load config instead of default:
                    if single_config.HasConfigKey(entry.key):
                        value = single_config.GetConfigValue(entry.key)
                        if entry.question_type == "secret":
                            value = "*" * len(value)
                    else:
                        value = entry.default

                    # Nice display for None:
                    if value is None:
                        value = ""

                    choices.append({
                        "name": f"{entry.name}: {value}",
                        "value": entry.key
                    })

            choice = self.DisplayMenu(
                choices=choices,
                message="Select config to edit")

            if choice == CHOICE_GO_BACK:
                return
            else:
                q_preset = preset.GetPresetByKey(choice)
                if q_preset:
                    self.EditSinglePreset(q_preset, single_config)
                    self.EditActiveConfiguration(typeClass, single_config)
                else:
                    self.DisplayMessage(f"Question preset not found: {choice}")

        else:
            self.DisplayMessage(
                f"No configuration for this {single_config.GetClassKey().capitalize()} :)")

    def EditSinglePreset(self, q_preset: QuestionPreset, single_config: SingleConfiguration):
        """ UI for changing a single setting """

        try:
            # Load config as default:
            if single_config.HasConfigKey(q_preset.key):
                if q_preset.default and q_preset.question_type != "yesno":
                    q_preset.instruction = f"Default: {q_preset.default}"
                q_preset.default = single_config.GetConfigValue(q_preset.key)

            value = q_preset.Ask()

            # If no default and not changed, do not save:
            if value or q_preset.default is not None:
                # Add to config:
                single_config.UpdateConfigValue(q_preset.key, value)

        except UserCancelledException:
            self.DisplayMessage("Configuration cancelled", force_clear=True)

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

            # Check for pinned messages:
            if TerminalDetection.CheckTerminalSupportsSize() and self.pinned_lines > 0:

                # Lines of message and instruction if too long:
                if "instruction" in kwargs:
                    message_lines = TerminalDetection.CalculateNumberOfLines(
                        len(kwargs["instruction"]) + len(message) + 3)
                # Add only the line of the message:
                else:
                    message_lines = 1

                # Calculate nr of lines required to display:
                required_lines = len(choices) + \
                    self.pinned_lines + message_lines

                terminal_lines = TerminalDetection.GetTerminalLines()

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
