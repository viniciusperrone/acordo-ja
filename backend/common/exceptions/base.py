

class AppException(Exception):
    """Base exception for all exceptions raised by this package."""
    status_code = 400

    def __init__(self, message, code=None, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details
