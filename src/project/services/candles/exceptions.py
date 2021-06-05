class ServiceCandleException(Exception):
    ...


class ServiceCandleTimeoutException(ServiceCandleException):
    ...


class ServiceCandleClientException(ServiceCandleException):
    ...


class ServiceCandleRequestClientException(ServiceCandleException):
    def __init__(self, message: str = '', status_code: int = None):
        self.message = message
        self.status_code = status_code

    def __repr__(self):
        return self.message
