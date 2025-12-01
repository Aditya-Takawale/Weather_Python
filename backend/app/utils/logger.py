"""
Logging Configuration
Provides structured logging for the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..config.settings import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure application-wide logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level = log_level or settings.LOG_LEVEL
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=settings.LOG_FORMAT,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler (daily rotation can be added with RotatingFileHandler)
            logging.FileHandler(
                log_dir / f"weather_monitoring_{datetime.now().strftime('%Y%m%d')}.log"
            )
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured with level: %s", level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
