from __future__ import annotations

from InquirerPy import inquirer

from IoTuring.Exceptions.Exceptions import UserCancelledException


class QuestionPreset():

    def __init__(self,
                 name,
                 key,
                 default=None,
                 mandatory=False,
                 dependsOn={},
                 instruction="",
                 question_type="text",
                 choices=[]
                 ) -> None:
        self.name = name
        self.key = key
        self.default = default
        self.mandatory = mandatory
        self.dependsOn = dependsOn
        self.instruction = instruction
        self.question_type = question_type
        self.choices = choices
        self.value = None

        self.question = self.name
        if mandatory:
            self.question += " {!}"

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
                        if answered.value:
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
        self.cancelled = False

    def HasQuestions(self) -> bool:
        """Check if this preset has any questions to ask"""
        return bool(self.presets)

    def AddEntry(self,
                 name,
                 key,
                 default=None,
                 mandatory=False,
                 display_if_key_value={},
                 instruction="",
                 question_type="text",
                 choices=[]) -> None:
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
        - instruction: more text to show
        - question_type: text, secret, integer, filepath, select or yesno
        - choices: only for select question type
        """

        if question_type not in ["text", "secret", "select", "yesno", "integer", "filepath"]:
            raise Exception(f"Unknown question type: {question_type}")

        if question_type == "select" and not choices:
            raise Exception(f"Missing choices for question: {name}")

        # Add question to presets:
        self.presets.append(
            QuestionPreset(
                name=name,
                key=key,
                default=default,
                mandatory=mandatory,
                dependsOn=display_if_key_value,
                instruction=instruction,
                question_type=question_type,
                choices=choices
            ))

    def AskQuestions(self) -> None:
        """Ask all questions of this preset"""
        for q_preset in self.presets:
            # if the previous question was cancelled:

            try:

                # It should be displayed, ask question:
                if q_preset.ShouldDisplay(self):

                    question_options = {}

                    if q_preset.mandatory:
                        def validate(x): return bool(x)
                        question_options.update({
                            "validate": validate,
                            "invalid_message": "You must provide a value for this key"
                        })

                    question_options["message"] = q_preset.question + ":"

                    if q_preset.default is not None:
                        # yesno questions need boolean default:
                        if q_preset.question_type == "yesno":
                            question_options["default"] = \
                                bool(str(q_preset.default).lower()
                                     in BooleanAnswers.TRUE_ANSWERS)
                        elif q_preset.question_type == "integer":
                            question_options["default"] = int(q_preset.default)
                        else:
                            question_options["default"] = q_preset.default
                    else:
                        if q_preset.question_type == "integer":
                            # The default default is 0, overwrite to None:
                            question_options["default"] = None

                    # text:
                    prompt_function = inquirer.text

                    if q_preset.question_type == "secret":
                        prompt_function = inquirer.secret

                    elif q_preset.question_type == "yesno":
                        prompt_function = inquirer.confirm
                        question_options.update({
                            "filter": lambda x: "Y" if x else "N"
                        })

                    elif q_preset.question_type == "select":
                        prompt_function = inquirer.select
                        question_options.update({
                            "choices": q_preset.choices
                        })

                    elif q_preset.question_type == "integer":
                        prompt_function = inquirer.number
                        question_options["float_allowed"] = False

                    elif q_preset.question_type == "filepath":
                        prompt_function = inquirer.filepath

                    # Create the prompt:
                    prompt = prompt_function(
                        instruction=q_preset.instruction,
                        **question_options
                    )

                    # Handle escape keypress:
                    @prompt.register_kb("escape")
                    def _handle_esc(event):
                        prompt._mandatory = False
                        prompt._handle_skip(event)
                        # exception raised here catched by inquirer.
                        self.cancelled = True

                    value = prompt.execute()

                    if self.cancelled:
                        raise UserCancelledException

                    if value:
                        q_preset.value = value
                        # Add to answered questions:
                        self.results.append(q_preset)

            except UserCancelledException:
                raise UserCancelledException
            except Exception as e:
                print(f"Error while making question for {q_preset.name}:", e)

    def GetAnsweredPresetByKey(self, key: str) -> QuestionPreset | None:
        return next((entry for entry in self.results if entry.key == key), None)

    def GetDict(self) -> dict:
        """ Get a dict with keys and responses"""
        return {entry.key: entry.value for entry in self.results}

    def GetDefaults(self) -> dict:
        """ Get a dict of default values of keys """
        return {entry.key: entry.default for entry in self.presets}

    def AddTagQuestion(self):
        """ Add a Tag question (compulsory, no default) to the preset.
            Useful for entities that must have a tag because of their multi-instance possibility """
        self.AddEntry(name="Tag", key="tag", mandatory=True,
                      instruction="Alias, to recognize entity in configurations and warehouses")


class BooleanAnswers:
    TRUE_ANSWERS = ["y", "yes", "t", "true", "ok", "okay"]  # all lower !
