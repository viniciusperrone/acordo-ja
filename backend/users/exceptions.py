from common.exceptions import AppException


class EmailAlreadyExists(AppException):
    status_code = 409
    message = "Email already exists"

class UserNotFoundError(AppException):
    status_code = 404
    message = "User not found"
