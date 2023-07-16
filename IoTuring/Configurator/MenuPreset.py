from __future__ import annotations

class QuestionPreset():

    def __init__(self, name, key, default=None, mandatory=False, dependsOn={}, modify_value_callback=None) -> None:
        self.name = name
        self.key = key
        self.default = default
        self.mandatory = mandatory
        self.dependsOn = dependsOn
        self.modify_value_callback = modify_value_callback
        self.value = None

        # Build the question:
        question_parts = [f'Add value for "{self.name}"']
        if mandatory:
            question_parts.append("{!}")
        if default is not None:
            question_parts.append(f"[{str(default)}]")

        self.question = " ".join(question_parts) + ": "

    def SetValue(self, value) -> None:
        """Sanitize and set value for this question"""

        if value and self.modify_value_callback:
            value = self.modify_value_callback(value)

        self.value = value

    def ShouldDisplay(self, menupreset: "MenuPreset") -> bool:
        """Check if this question should be displayed"""

        should_display = True

        # Check if it has dependencies:
        if self.dependsOn:
            dependencies_ok = []
            for key, value in self.dependsOn.items():
                answered = menupreset.GetAnsweredPresetByKey(key)
                dependency_ok = False

                # Found the key in results:
                if answered:

                    # Value is True or False:
                    if isinstance(value, bool):
                        if (answered.value == answered.default) != value:
                            dependency_ok = True

                    # Value must match:
                    elif isinstance(value, str) and answered.value == value:
                        dependency_ok = True

                dependencies_ok.append(dependency_ok)

            # All should be True:
            if not all(dependencies_ok):
                should_display = False

        return should_display


class MenuPreset():

    def __init__(self) -> None:
        self.presets: list[QuestionPreset] = []
        self.results: list[QuestionPreset] = []

    def HasQuestions(self) -> bool:
        """Check if this preset has any questions to ask"""
        return bool(self.presets)

    def AddEntry(self, name, key, default=None, mandatory=False, display_if_key_value={}, modify_value_callback=None) -> None:
        """ 
        Add an entry to the preset with:
        - key: the key to use in the dict
        - name: the name to display to the user
        - default: the default value to use if the user doesn't provide one (works only if mandatory=False)
        - mandatory: if the user must provide a value for this entry
        - display_if_key_value: dict of a key and value another entry (that must preceed this) that will enable this one:
          * Default empty dict: the entry will be always displayed
          * In the dict each key is a key of a previous entry.
          * If the value is a string, this entry will be enabled, if the value is the same as the of answer that question
          * If the value is True this entry will be enabled if anything was answered
          * If the value if False, it will be displayed, if nothing was answered to that question.
          * In case this won't be displayed, a default value will be used if provided; otherwise won't set this key in the dict)
        ! Caution: if the entry is not displayed, the mandatory property will be ignored !
        - modify_value_callback: a callback to modify the value before it's set in the dict (called also for a default value). The callback must have the following signature: NAME(value) -> value
        """

        # Add question to presets:
        self.presets.append(
            QuestionPreset(
                name=name,
                key=key,
                default=default,
                mandatory=mandatory,
                dependsOn=display_if_key_value,
                modify_value_callback=modify_value_callback
            ))

    def AskQuestions(self) -> None:
        """Ask all questions of this preset"""
        for q_preset in self.presets:
            try:
                value = None

                # It should be displayed, ask question:
                if q_preset.ShouldDisplay(self):
                    value = input(q_preset.question)

                    # Mandatory loop:
                    while value == "" and q_preset.mandatory:
                        value = input(
                            "You must provide a value for this key: ")

                    # Set default:
                    if value == "":
                        value = q_preset.default

                # It should not be displayed:
                else:
                    # It's already answered:
                    if self.GetAnsweredPresetByKey(q_preset.key):
                        continue

                    # Set default value otherwise:
                    else:
                        value = q_preset.default

                # Set and sanitize the value:
                q_preset.SetValue(value)
                # Add to answered questions:
                self.results.append(q_preset)

            except Exception as e:
                print("Error while making the question:", e)

    def GetAnsweredPresetByKey(self, key: str) -> QuestionPreset | None:
        return next((entry for entry in self.results if entry.key == key), None)

    def GetDict(self) -> dict:
        """ Get a dict with keys and responses"""
        return {entry.key: entry.value for entry in self.results}

    def GetDefaults(self) -> dict:
        """ Get a dict of default values of keys """
        return {entry.key: entry.default for entry in self.presets}

    @staticmethod
    def PrintRules() -> None:
        """ Print configuration rules, like a legend for complusory symbol and default values """
        print("\n\t-- Rules --")
        print("\t\tIf you see {!} then the value is complusory")
        print(
            "\t\tIf you see [ ] then the value in the brackets is the default one: leave blank the input to use that value")
        print(
            "\t\tIf a tag is asked, it is an alias for the entity to recognize it in configurations and warehouses")
        print("\t-- End of rules --\n")

    def AddTagQuestion(self):
        """ Add a Tag question (compulsory, no default) to the preset.
            Useful for entities that must have a tag because of their multi-instance possibility """
        self.AddEntry("Tag", "tag", mandatory=True,
                      modify_value_callback=normalize_tag)

    @staticmethod
    def Callback_NormalizeBoolean(value):
        """ Normalize a boolean value to be used, given a string from user input. To be used as MenuPreset callback. """
        if value.lower() in BooleanAnswers.TRUE_ANSWERS:
            return True
        return False

    @staticmethod
    def Callback_LowerAndStripString(value) -> str:
        """ Remove spaces from a string end, make lowercase """
        return str(value).lower().strip()


def normalize_tag(tag):
    """ Normalize a tag to be used safely"""
    return tag.lower().replace(" ", "_")


class BooleanAnswers:
    TRUE_ANSWERS = ["y", "yes", "t", "true", "ok", "okay"]  # all lower !
