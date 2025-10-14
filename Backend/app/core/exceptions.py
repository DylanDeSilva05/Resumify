"""
Custom exception classes
"""
from fastapi import HTTPException


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with error codes"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: dict = None
    ):
        super().__init__(status_code, detail, headers)
        self.error_code = error_code


class AuthenticationError(CustomHTTPException):
    """Authentication related errors"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTH_ERROR"
        )


class AuthorizationError(CustomHTTPException):
    """Authorization related errors"""

    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="AUTH_ERROR"
        )


class ValidationError(CustomHTTPException):
    """Input validation errors"""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class NotFoundError(CustomHTTPException):
    """Resource not found errors"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND"
        )


class ConflictError(CustomHTTPException):
    """Resource conflict errors"""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="CONFLICT"
        )


class FileProcessingError(CustomHTTPException):
    """File processing related errors"""

    def __init__(self, detail: str = "File processing failed"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="FILE_PROCESSING_ERROR"
        )