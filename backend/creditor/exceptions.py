from common.exceptions import AppException


class CreditorAlreadyExistsError(AppException):
    message = "Creditor already exists"
    status_code = 400

class CreditorNotFound(AppException):
    message = "Creditor not found"
    status_code = 404