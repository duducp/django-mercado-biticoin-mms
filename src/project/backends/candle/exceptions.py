class CandleError(Exception):
    pass


class CandleTimeoutError(CandleError):
    pass


class CandleClientError(CandleError):
    pass


class CandleRequestClientError(CandleError):
    def __init__(
        self,
        message: str = '',
        status_code: int = None,
        response: str = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response

    def __repr__(self):
        return self.message
