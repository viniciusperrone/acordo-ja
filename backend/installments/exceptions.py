from common.exceptions import AppException


class InstallmentError(AppException):
    pass

class InstallmentNotFound(InstallmentError):
    message = "Installment not found"
    status_code = 404

class InstallmentWithoutAgreement(InstallmentError):
    message = "Installment with no agreement"
    status_code = 400
