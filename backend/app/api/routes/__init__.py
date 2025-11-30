"""API routes for the Weather Monitoring System"""

from .dashboard import router as dashboard_router
from .weather import router as weather_router
from .alerts import router as alerts_router

__all__ = [
    "dashboard_router",
    "weather_router",
    "alerts_router"
]
