import re

class MenuPreset():

    def __init__(self) -> None:
        self.preset = []
        self.result = []

    def AddEntry(self, name, key, default=None, mandatory=False, display_if_key_value_regex_match=None, modify_value_callback=None):
        """ 
        Add an entry to the preset with:
        - key: the key to use in the dict
        - name: the name to display to the user
        - default: the default value to use if the user doesn't provide one (works only if mandatory=False)
        - mandatory: if the user must provide a value for this entry
        - display_if_key_value_regex_match: dict of a key and value regex of an entry (that must preceed this) that will enable this one, if the provided value of that key matches the value regex
          * If it's None, the entry will always be displayed
          * If value of the key doesn't match the regex, it won't be displayed
          * If value of a key is a boolean True it will be displayed if anything was given
          * In case this won't be displayed, a default value will be used if provided; otherwise won't set this key in the dict)
        ! Caution: if the entry is not displayed, the mandatory property will be ignored !
        - modify_value_callback: a callback to modify the value before it's set in the dict (called also for a default value). The callback must have the following signature: NAME(value) -> value
        """
        self.preset.append(
            {"name": name, "key": key, "default": default, "mandatory": mandatory, "dependsOn": display_if_key_value_regex_match, "modify_value_callback": modify_value_callback, "value": None})

    def ListEntries(self):
        return self.preset

    def Question(self, id):
        try:
            question = ""
            value = None
            if id < len(self.preset):
                shouldDisplay = True

                # Check previous entry regexes:
                if self.preset[id]["dependsOn"]:
                    matches = []
                    # Multiple rules are possible:
                    for key in self.preset[id]["dependsOn"]:
                        # If value is True, anything ok:
                        if type(self.preset[id]["dependsOn"][key]) is bool and \
                                self.preset[id]["dependsOn"][key]:
                            matches.append(bool(self.RetrievePresetAnswerByKey(key)))
                        else:
                            # Check if regex matches:
                            matches.append(re.search(self.preset[id]["dependsOn"][key], str(
                                self.RetrievePresetAnswerByKey(key))))
                    # All should match:
                    if not all(matches):
                        shouldDisplay = False

                # ask for a value:
                if shouldDisplay:
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
                            value = self.preset[id]["default"]
                        else:
                            value = None 
                    # else value already in value

                # If it already has value from another question:
                elif self.preset[id]['key'] in [ r['key'] for r in self.result]:
                    return

                # If the entry is not displayed, set the default value if provided
                elif self.preset[id]["default"]: # if I have a default    
                    # Set in the preset
                    value = self.preset[id]["default"]
                
                    
                # if a callback is provided, use it to modify the value
                if value and self.preset[id]["modify_value_callback"]:
                    value = self.preset[id]["modify_value_callback"](value)

                self.preset[id]['value'] = value
                # move the answered question to results:
                self.result.append(self.preset[id])
                
                    
        except Exception as e:
            print("Error while making the question:", e)

    def RetrievePresetAnswerByKey(self, key):
        for entry in self.result:
            if entry['key'] == key:
                return entry['value']
        return None

    def GetDict(self) -> dict:
        """ Get a dict with keys and responses"""
        return {entry['key']: entry['value'] for entry in self.result}

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
        self.AddEntry("Tag", "tag", mandatory=True, modify_value_callback=normalize_tag)



    @staticmethod 
    def Callback_NormalizeBoolean(value):
        """ Normalize a boolean value to be used, given a string from user input. To be used as MenuPreset callback. """
        if value.lower() in BooleanAnswers.TRUE_ANSWERS:
            return True
        return False

def normalize_tag(tag):
    """ Normalize a tag to be used safely"""
    return tag.lower().replace(" ", "_")


class BooleanAnswers:
    TRUE_ANSWERS = ["y", "yes", "t", "true", "ok", "okay"]  # all lower !
