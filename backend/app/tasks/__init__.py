"""Celery tasks for scheduled background jobs"""

from .celery_app import celery_app
from .weather_tasks import fetch_weather_data
from .dashboard_tasks import populate_dashboard_summary
from .cleanup_tasks import cleanup_old_data
from .alert_tasks import check_weather_alerts

__all__ = [
    "celery_app",
    "fetch_weather_data",
    "populate_dashboard_summary",
    "cleanup_old_data",
    "check_weather_alerts"
]
