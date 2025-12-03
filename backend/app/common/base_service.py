"""
Base Service Class
Business logic layer with dependency injection
"""

from typing import Generic, TypeVar, Optional
from ..core.logging import get_logger

T = TypeVar('T')


class BaseService(Generic[T]):
    """
    Generic service base class
    Handles business logic and orchestrates repository calls
    """
    
    def __init__(self):
        """Initialize service with logger"""
        self.logger = get_logger(self.__class__.__name__)
    
    def _log_info(self, message: str, *args):
        """Log info message"""
        self.logger.info(message, *args)
    
    def _log_error(self, message: str, *args):
        """Log error message"""
        self.logger.error(message, *args)
    
    def _log_warning(self, message: str, *args):
        """Log warning message"""
        self.logger.warning(message, *args)
    
    def _validate_required_fields(self, data: dict, required_fields: list) -> Optional[str]:
        """
        Validate required fields in data
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            Error message if validation fails, None otherwise
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        
        return None
