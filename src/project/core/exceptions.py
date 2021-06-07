from http import HTTPStatus

from ninja.errors import HttpError


class NotFoundError(HttpError):
    def __init__(self, message: str) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, message)


class UnauthorizedError(HttpError):
    def __init__(self, message: str) -> None:
        super().__init__(HTTPStatus.UNAUTHORIZED, message)


class ConflictError(HttpError):
    def __init__(self, message: str) -> None:
        super().__init__(HTTPStatus.CONFLICT, message)


class InternalServerError(HttpError):
    def __init__(self, message: str) -> None:
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message)
