

class AppException(Exception):
    """Base exception for all exceptions raised by this package."""
    status_code = 400
    message = "Unexpected error"

    def __init__(self, message=None, code=None, details=None):
        super().__init__(message)
        self.message = message or self.message
        self.code = code
        self.details = details
