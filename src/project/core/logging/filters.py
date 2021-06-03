import logging


class IgnoreIfContains(logging.Filter):
    """
    Ignore log record if message entry contains any substring set on
    log filter configuration.
    """

    def __init__(self, substrings=None):
        super().__init__()
        self.substrings = substrings or []

    def filter(self, record):
        message = record.getMessage()

        return not any(
            substring in message
            for substring in self.substrings
        )
