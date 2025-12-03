"""
Core Module
Shared infrastructure components including Celery, logging, and utilities
"""

from .celery import celery_app
from .logging import setup_logging, get_logger
from .utils import (
    get_current_timestamp,
    format_temperature,
    kelvin_to_celsius,
    celsius_to_fahrenheit,
    calculate_feels_like,
    truncate_string,
    safe_float,
    safe_int
)

__all__ = [
    # Celery
    'celery_app',
    
    # Logging
    'setup_logging',
    'get_logger',
    
    # Utilities
    'get_current_timestamp',
    'format_temperature',
    'kelvin_to_celsius',
    'celsius_to_fahrenheit',
    'calculate_feels_like',
    'truncate_string',
    'safe_float',
    'safe_int'
]
