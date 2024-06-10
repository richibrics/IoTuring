class UnknownEntityKeyException(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(f"Unknown entity key: {key}")


class UnknownConfigKeyException(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(f"Configuration key not found: {key}")


class UserCancelledException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.message = "User cancelled the ongoing process"


class UnknownLoglevelException(Exception):
    def __init__(self, loglevel: str) -> None:
        super().__init__(f"Unknown log level: {loglevel}")
        self.loglevel = loglevel
