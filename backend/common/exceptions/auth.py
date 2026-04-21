from .base import AppException


class UnauthorizedError(AppException):
    status_code = 401
    message = "Unauthorized"
