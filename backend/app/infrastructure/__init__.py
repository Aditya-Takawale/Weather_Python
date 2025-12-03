"""
Infrastructure Module
External systems and configuration management

This module handles:
- Configuration (settings, environment variables)
- Database connections (MongoDB)
- External service clients (planned: Redis, OpenWeatherMap)
"""

from .config import settings, Settings
from .database import DatabaseManager

__all__ = [
    'settings',
    'Settings',
    'DatabaseManager'
]
