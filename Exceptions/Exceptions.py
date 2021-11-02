class UnknownKeyException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.message = "This key isn't registered in this entity"
