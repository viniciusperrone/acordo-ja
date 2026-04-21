from common.exceptions import AppException


class InvalidCredentials(AppException):
    status_code = 401
    message = "Invalid credentials"
