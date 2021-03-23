class PYRApplicationError(Exception):
    """
    Error to raise in case of now you rest application errors.
    """

    def __init__(self, error_message, user_message=None, extra_params={}):
        self.error_message = error_message
        self.user_message = user_message
        self.extra_params = extra_params
