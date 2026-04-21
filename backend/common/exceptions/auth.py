from .base import AppException


class UnauthorizedError(AppException):
    status_code = 401

    def __init__(self, message="Unauthorized"):
        super().__init__(
            message=message
        )
