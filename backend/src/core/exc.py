class DuplicateEntryError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class InvalidPasswordError(ValueError):
    def __init__(self, message):
        super().__init__(message)
