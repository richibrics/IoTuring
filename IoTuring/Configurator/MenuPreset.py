class MenuPreset():

    def __init__(self) -> None:
        self.preset = []

    def AddEntry(self, name, key, default=None, mandatory=False):
        self.preset.append(
            {"name": name, "key": key, "default": default, "mandatory": mandatory, "value": None})

    def ListEntries(self):
        return self.preset

    def Question(self, id):
        try:
            question = ""
            if id < len(self.preset):
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
        except Exception as e:
            print("Error while making the question:", e)

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
