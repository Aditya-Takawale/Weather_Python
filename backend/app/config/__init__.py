"""Configuration module for the Weather Monitoring System"""

from .settings import settings
from .database import get_database, close_database_connection

__all__ = ["settings", "get_database", "close_database_connection"]
