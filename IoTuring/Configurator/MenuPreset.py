class MenuPreset():

    def __init__(self) -> None:
        self.preset = []

    def AddEntry(self, name, key, default=None, mandatory=False, display_if_value_for_following_key_provided=None):
        """ 
        Add an entry to the preset with:
        - key: the key to use in the dict
        - name: the name to display to the user
        - default: the default value to use if the user doesn't provide one (works only if mandatory=False)
        - mandatory: if the user must provide a value for this entry
        - display_if_value_for_following_key_provided: key of an entry (that must preceed this) that will enable this one, if the user has provided a value for that.
          * If it's None, the entry will always be displayed
          * If it has a key, the entry won't be displayed if menu[provided_key] has value.
          * In case this won't be displayed, a default value will be used if provided; otherwise won't set this key in the dict)
        ! Caution: if the entry is not displayed, the mandatory property will be ignored !
        """
        self.preset.append(
            {"name": name, "key": key, "default": default, "mandatory": mandatory, "dependsOn": display_if_value_for_following_key_provided, "value": None})

    def ListEntries(self):
        return self.preset

    def Question(self, id):
        try:
            question = ""
            if id < len(self.preset):
                # if the display of this does not depend on a previous entry, or if the previous entry (this depends on) has a value: ask for a value
                if self.preset[id]["dependsOn"] is None or self.RetrievePresetAnswerByKey(self.preset[id]["dependsOn"]): 
                    question = "Add value for \""+self.preset[id]["name"]+"\""
                    if self.preset[id]['mandatory']:
                        question = question + " {!}"
                    if self.preset[id]["default"] is not None:
                        question = question + \
                            " [" + str(self.preset[id]["default"])+"]"

                    question = question + ": "

                    value = input(question)

                    # Mandatory loop
                    while value == "" and self.preset[id]["mandatory"]:
                        value = input("You must provide a value for this key: ")

                    if value == "":
                        if self.preset[id]["default"] is not None:
                            # Set in the preset
                            self.preset[id]['value'] = self.preset[id]["default"]
                            return self.preset[id]["default"]  # Also return it
                        else:
                            self.preset[id]['value'] = None  # Set in the preset
                            return None  # Also return it
                    else:
                        self.preset[id]['value'] = value  # Set in the preset
                        return value  # Also return it
                else: 
                    # If the entry is not displayed, set the default value if provided
                    if self.preset[id]["default"]: # if I have a default
                        # Set in the preset
                        self.preset[id]['value'] = self.preset[id]["default"]
                        return self.preset[id]["default"]  # Also return it
                    else:
                        return None # don't set anything
                    
        except Exception as e:
            print("Error while making the question:", e)

    def RetrievePresetAnswerByKey(self, key):
        for entry in self.preset:
            if entry['key'] == key:
                return entry['value']
        return None

    def GetDict(self) -> dict:
        """ Get a dict with keys and responses"""
        result = {}
        for entry in self.preset:
            result[entry['key']] = entry['value']
        return result

    @staticmethod
    def PrintRules() -> None:
        """ Print configuration rules, like a legend for complusory symbol and default values """
        print("\n\t-- Rules --")
        print("\t\tIf you see {!} then the value is complusory")
        print(
            "\t\tIf you see [ ] then the value in the brackets is the default one: leave blank the input to use that value")
        print("\t-- End of rules --\n")

    def AddTagQuestion(self):
        """ Add a Tag question (compulsory, no default) to the preset.
            Useful for entities that must have a tag because of their multi-instance possibility """
        self.AddEntry("Tag", "tag", mandatory=True)


class BooleanAnswers:
    TRUE_ANSWERS = ["y", "yes", "t", "true", "ok", "okay"]  # all lower !
