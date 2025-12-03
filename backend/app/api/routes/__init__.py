"""
API routes for the Weather Monitoring System
Updated to use OOP architecture with routers from feature modules
"""

# Import routers from new OOP structure
from ..weather.weather_router import router as weather_router
from ..dashboard.dashboard_router import router as dashboard_router
from ..alerts.alert_router import router as alerts_router

__all__ = [
    "dashboard_router",
    "weather_router",
    "alerts_router"
]
