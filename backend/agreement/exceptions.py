from common.exceptions import AppException


class AgreementNotFound(AppException):
    status_code = 404
    message = "Agreement not found"

class AgreementStatusError(AppException):
    status_code = 400
    message = None

class PendingInstallmentsError(Exception):
    status_code = 400
    message = "There are outstanding installments"
