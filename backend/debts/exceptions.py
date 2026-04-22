from common.exceptions import AppException


class DebtNotFound(AppException):
    status_code = 404
    message = "Debt not found"
