"""
Decorators for logging, validation, and error handling
"""

import functools
import time
from typing import Any, Callable
from ..core.logging import get_logger
from .exceptions import ValidationException, InternalServerException


def log_execution(func: Callable) -> Callable:
    """
    Decorator to log method execution time and details
    
    Usage:
        @log_execution
        async def my_method(self):
            pass
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Get logger from instance if available
        instance = args[0] if args else None
        logger = getattr(instance, 'logger', None) or get_logger(func.__name__)
        
        # Log method call
        method_name = func.__name__
        class_name = instance.__class__.__name__ if instance else 'Unknown'
        logger.info(f"Executing {class_name}.{method_name}")
        
        # Measure execution time
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Completed {class_name}.{method_name} in {execution_time:.2f}s")
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Failed {class_name}.{method_name} after {execution_time:.2f}s: {str(e)}",
                exc_info=True
            )
            raise
    
    return wrapper


def validate_input(**validators) -> Callable:
    """
    Decorator to validate input parameters
    
    Usage:
        @validate_input(
            city=lambda x: x and len(x) > 0,
            temperature=lambda x: -100 <= x <= 100
        )
        async def my_method(self, city: str, temperature: float):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not validator(value):
                        raise ValidationException(
                            message=f"Invalid value for parameter '{param_name}'",
                            details={"parameter": param_name, "value": str(value)}
                        )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle exceptions and convert to HTTP exceptions
    
    Usage:
        @handle_exceptions
        async def my_method(self):
            pass
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        instance = args[0] if args else None
        logger = getattr(instance, 'logger', None) or get_logger(func.__name__)
        
        try:
            return await func(*args, **kwargs)
        
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)
            
            # Re-raise if already an HTTP exception
            if hasattr(e, 'status_code'):
                raise
            
            # Convert to internal server error
            raise InternalServerException(
                message=str(e),
                details={
                    "function": func.__name__,
                    "exception_type": type(e).__name__
                }
            )
    
    return wrapper


def require_fields(*required_fields: str) -> Callable:
    """
    Decorator to validate required fields in data dictionary
    
    Usage:
        @require_fields('city', 'temperature')
        async def my_method(self, data: dict):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find data parameter
            data = None
            
            # Check kwargs
            if 'data' in kwargs:
                data = kwargs['data']
            # Check args (assume second arg after self)
            elif len(args) > 1:
                data = args[1]
            
            if data is None:
                raise ValidationException(
                    message="No data provided",
                    details={"required_fields": list(required_fields)}
                )
            
            # Validate required fields
            missing_fields = [
                field for field in required_fields
                if field not in data or data[field] is None
            ]
            
            if missing_fields:
                raise ValidationException(
                    message=f"Missing required fields: {', '.join(missing_fields)}",
                    details={
                        "missing_fields": missing_fields,
                        "required_fields": list(required_fields)
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def cache_result(ttl_seconds: int = 300) -> Callable:
    """
    Decorator to cache method results
    
    Args:
        ttl_seconds: Time to live in seconds
        
    Usage:
        @cache_result(ttl_seconds=60)
        async def my_method(self):
            pass
    """
    cache_store = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            if cache_key in cache_store:
                cached_data, cached_time = cache_store[cache_key]
                if time.time() - cached_time < ttl_seconds:
                    return cached_data
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_store[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    
    return decorator
