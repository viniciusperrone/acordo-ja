from .base import AppException


class UnauthorizedError(AppException):
    status_code = 401
    message = "Unauthorized"

class ForbiddenError(AppException):
    status_code = 403
    message = "Forbidden"
