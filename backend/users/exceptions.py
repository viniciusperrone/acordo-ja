from common.exceptions import AppException


class EmailAlreadyExists(AppException):
    status_code = 409

    def __init__(self, message="Email already exists"):
        super().__init__(message=message, code="EMAIL_ALREADY_EXIST")

class UserNotFoundError(Exception):
    pass