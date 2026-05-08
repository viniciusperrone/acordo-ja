from common.exceptions import AppException


class DebtNotFound(AppException):
    message = "Debt not found"
    status_code = 404
