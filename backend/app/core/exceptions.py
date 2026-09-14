"""
Domain-level exceptions.

Services and repositories raise these instead of HTTPException so that
business logic stays framework-agnostic. The API layer (middleware/
exception_handlers.py) translates them into proper HTTP responses.
"""


class AppException(Exception):
    """Base class for all application (domain) exceptions."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str = "An unexpected error occurred", **details):
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    status_code = 404
    error_code = "not_found"


class AlreadyExistsError(AppException):
    status_code = 409
    error_code = "already_exists"


class ValidationError(AppException):
    status_code = 422
    error_code = "validation_error"


class AuthenticationError(AppException):
    status_code = 401
    error_code = "authentication_error"


class InvalidCredentialsError(AuthenticationError):
    error_code = "invalid_credentials"

    def __init__(self, message: str = "Incorrect email or password"):
        super().__init__(message)


class TokenError(AuthenticationError):
    error_code = "invalid_token"


class TokenExpiredError(TokenError):
    error_code = "token_expired"

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class AuthorizationError(AppException):
    status_code = 403
    error_code = "authorization_error"

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message)


class InactiveUserError(AuthenticationError):
    error_code = "inactive_user"

    def __init__(self, message: str = "This account is inactive"):
        super().__init__(message)


class UnverifiedEmailError(AuthenticationError):
    error_code = "email_not_verified"

    def __init__(self, message: str = "Please verify your email before logging in"):
        super().__init__(message)


class RateLimitExceededError(AppException):
    status_code = 429
    error_code = "rate_limit_exceeded"

    def __init__(self, message: str = "Too many requests, please try again later"):
        super().__init__(message)


# Compatibility exceptions retained from the resume-analyzer module.
class NotFoundException(NotFoundError):
    pass

class ForbiddenException(AuthorizationError):
    pass

class UnauthorizedException(AuthenticationError):
    pass

class ValidationException(ValidationError):
    pass

class ConflictException(AlreadyExistsError):
    pass

class FileValidationError(ValidationError):
    status_code = 400

class AIServiceError(AppException):
    status_code = 502
    error_code = "ai_service_error"

class StorageError(AppException):
    status_code = 500
    error_code = "storage_error"
