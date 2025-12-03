"""
Base Controller Class
HTTP request/response handling layer
"""

from typing import Any, Dict, Optional
from fastapi import Response, status
from ..core.logging import get_logger
from .exceptions import BaseHTTPException, InternalServerException


class BaseController:
    """
    Base controller for HTTP request/response handling
    Provides standardized response formatting
    """
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = get_logger(self.__class__.__name__)
    
    def success_response(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK
    ) -> Dict[str, Any]:
        """
        Create standardized success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            
        Returns:
            Formatted success response
        """
        response = {
            "success": True,
            "message": message,
            "status_code": status_code
        }
        
        if data is not None:
            response["data"] = data
        
        return response
    
    def error_response(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            message: Error message
            error_code: Error code identifier
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            Formatted error response
        """
        response = {
            "success": False,
            "message": message,
            "status_code": status_code
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response
    
    def handle_exception(self, exception: Exception) -> Dict[str, Any]:
        """
        Handle exceptions and convert to HTTP response
        
        Args:
            exception: Exception to handle
            
        Returns:
            Formatted error response
        """
        # Log the exception
        self.logger.error(f"Exception occurred: {str(exception)}", exc_info=True)
        
        # Handle custom HTTP exceptions
        if isinstance(exception, BaseHTTPException):
            return exception.to_dict()
        
        # Handle unknown exceptions
        internal_error = InternalServerException(
            message=str(exception),
            details={"exception_type": type(exception).__name__}
        )
        
        return internal_error.to_dict()
    
    async def execute_service_call(
        self,
        service_method,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute service method with exception handling
        
        Args:
            service_method: Service method to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Success or error response
        """
        try:
            result = await service_method(*args, **kwargs)
            return self.success_response(data=result)
        
        except BaseHTTPException as e:
            return self.handle_exception(e)
        
        except Exception as e:
            return self.handle_exception(e)
