class UnknownEntityKeyException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.message = "This key isn't registered in any entity data"


class UserCancelledException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.message = "User cancelled the ongoing process"


class UnknownLoglevelException(Exception):
    def __init__(self, loglevel: str) -> None:
        super().__init__(f"Unknown log level: {loglevel}")
        self.loglevel = loglevel