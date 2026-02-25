

class InstallmentError(Exception):
    pass

class InstallmentNotFoundError(InstallmentError):
    pass

class InstallmentWithoutAgreementError(InstallmentError):
    pass