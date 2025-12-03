"""
Celery Application Configuration
Configures Celery with Beat scheduler for periodic tasks
"""

from celery import Celery
from celery.schedules import crontab
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import settings

# Create Celery app
celery_app = Celery(
    "weather_monitoring",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Celery Beat schedule configuration
celery_app.conf.beat_schedule = {
    # Task 1: Fetch weather data every 10 minutes
    'fetch-weather-data': {
        'task': 'api.weather.tasks.fetch_weather_data',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'args': (settings.OPENWEATHER_CITY,),
        'options': {'queue': 'weather_queue'}
    },
    
    # Task 2: Populate dashboard summary every hour
    'populate-dashboard-summary': {
        'task': 'api.dashboard.tasks.populate_dashboard_summary',
        'schedule': crontab(minute=0),  # Every hour at :00
        'args': (settings.OPENWEATHER_CITY,),
        'options': {'queue': 'dashboard_queue'}
    },
    
    # Task 3: Cleanup old data daily at 2 AM
    'cleanup-old-data': {
        'task': 'core.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
        'args': (settings.DATA_RETENTION_DAYS,),
        'options': {'queue': 'maintenance_queue'}
    },
    
    # Task 4: Check weather alerts every 15 minutes
    'check-weather-alerts': {
        'task': 'api.alerts.tasks.check_weather_alerts',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'args': (settings.OPENWEATHER_CITY,),
        'options': {'queue': 'alert_queue'}
    },
}

# Auto-discover tasks in all modules
celery_app.autodiscover_tasks([
    'app.api.weather.tasks',
    'app.api.dashboard.tasks',
    'app.api.alerts.tasks',
    'app.core.tasks'
])

# Configure task routes
celery_app.conf.task_routes = {
    'api.weather.tasks.*': {'queue': 'weather_queue'},
    'api.dashboard.tasks.*': {'queue': 'dashboard_queue'},
    'api.alerts.tasks.*': {'queue': 'alert_queue'},
    'core.tasks.*': {'queue': 'maintenance_queue'},
}
