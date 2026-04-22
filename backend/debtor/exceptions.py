from common.exceptions import AppException

class DebtorNotFound(AppException):
    message = "Debtor not found"
    status_code = 404

class DuplicateDocumentDebtor(AppException):
    message = "Duplicate document debtor"
    status_code = 409
