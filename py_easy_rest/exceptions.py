class PYRNotFoundError(Exception):
    """
    Exception to raise in case of entity not found.
    """

    def __init__(self, message):
        self.message = message


class PYRInputNotValidError(Exception):
    """
    Exception to raise in case of input not valid.
    """

    def __init__(self, message):
        self.message = message
