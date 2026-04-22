from common.exceptions import AppException


class PaymentError(AppException):
    message = None
    status_code = 400
