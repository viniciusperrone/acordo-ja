from common.exceptions import AppException


class InvalidCredentials(AppException):
    status_code = 401
    message = "Invalid credentials"

class InvalidPasswordResetToken(AppException):
    status_code = 400
    message = "Invalid or expired token"

class MissingTokenIdentifier(AppException):
    status_code = 400
    message = "Token identifier (jti) was not provided"
