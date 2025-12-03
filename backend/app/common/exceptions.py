"""
Custom HTTP Exception Classes
Similar to Node.js httpErrorClasses pattern
"""

from typing import Any, Dict, Optional


class BaseHTTPException(Exception):
    """Base HTTP exception class"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }


class BadRequestException(BaseHTTPException):
    """400 Bad Request"""
    def __init__(self, message: str = "Bad Request", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class UnauthorizedException(BaseHTTPException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Unauthorized", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class ForbiddenException(BaseHTTPException):
    """403 Forbidden"""
    def __init__(self, message: str = "Forbidden", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class NotFoundException(BaseHTTPException):
    """404 Not Found"""
    def __init__(self, message: str = "Resource Not Found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class ConflictException(BaseHTTPException):
    """409 Conflict"""
    def __init__(self, message: str = "Conflict", **kwargs):
        super().__init__(message, status_code=409, **kwargs)


class ValidationException(BaseHTTPException):
    """422 Unprocessable Entity"""
    def __init__(self, message: str = "Validation Failed", **kwargs):
        super().__init__(message, status_code=422, **kwargs)


class InternalServerException(BaseHTTPException):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal Server Error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class ServiceUnavailableException(BaseHTTPException):
    """503 Service Unavailable"""
    def __init__(self, message: str = "Service Unavailable", **kwargs):
        super().__init__(message, status_code=503, **kwargs)
