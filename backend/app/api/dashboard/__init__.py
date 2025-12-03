"""Dashboard module with OOP architecture"""

from .dashboard_repository import DashboardRepository
from .dashboard_service import DashboardService
from .dashboard_controller import DashboardController
from .dashboard_router import router

__all__ = [
    "DashboardRepository",
    "DashboardService",
    "DashboardController",
    "router"
]
