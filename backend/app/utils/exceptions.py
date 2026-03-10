class AppException(Exception):
    """
    Base exception for application errors.
    """

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BadRequestException(AppException):
    """
    Raised for invalid requests (400).
    """
    pass


class NotFoundException(AppException):
    """
    Raised when resource does not exist (404).
    """
    pass


class UnauthorizedException(AppException):
    """
    Raised when authentication fails (401).
    """
    pass


class ForbiddenException(AppException):
    """
    Raised when user lacks permissions (403).
    """
    pass