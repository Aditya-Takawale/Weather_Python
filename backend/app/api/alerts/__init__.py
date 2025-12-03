"""Alerts module with OOP architecture"""

from .alert_repository import AlertRepository
from .alert_service import AlertService
from .alert_controller import AlertController
from .alert_router import router

__all__ = [
    "AlertRepository",
    "AlertService",
    "AlertController",
    "router"
]
