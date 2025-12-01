"""
Weather Data Fetching Tasks
Celery tasks for fetching weather data from OpenWeatherMap API
"""

import asyncio
from celery import Task
from .celery_app import celery_app
from ..config.database import DatabaseManager
from ..services.weather_service import WeatherService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database connection lifecycle"""
    
    _db_connected = False
    
    def run(self, *args, **kwargs):
        """Placeholder run method - actual work done in concrete tasks"""
    
    def before_start(self, task_id, args, kwargs):
        """Connect to database before task starts"""
        if not self._db_connected:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(DatabaseManager.connect())
            self._db_connected = True
            logger.info("Database connected for Celery task")


@celery_app.task(
    name="app.tasks.weather_tasks.fetch_weather_data",
    base=DatabaseTask,
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def fetch_weather_data(self, city: str) -> dict:
    """
    Celery Task 1: Fetch weather data from OpenWeatherMap API
    Runs every 30 minutes
    
    Args:
        city: City name to fetch weather for
        
    Returns:
        Task result dictionary
    """
    logger.info("[WEATHER] Starting weather data fetch task for %s", city)
    
    try:
        # Run async service method
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(WeatherService.fetch_and_store_weather(city))
        
        if success:
            logger.info("[SUCCESS] Weather data fetch successful for %s", city)
            return {
                "status": "success",
                "city": city,
                "message": "Weather data fetched and stored successfully"
            }
        else:
            logger.error("[FAILED] Weather data fetch failed for %s", city)
            # Retry the task
            raise self.retry(exc=Exception("Failed to fetch weather data"))
            
    except Exception as exc:
        logger.error("[ERROR] Error in weather fetch task: %s", exc)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@celery_app.task(
    name="app.tasks.weather_tasks.fetch_weather_data_on_demand",
    base=DatabaseTask
)
def fetch_weather_data_on_demand(city: str) -> dict:
    """
    On-demand weather data fetch (can be triggered manually)
    
    Args:
        city: City name
        
    Returns:
        Task result
    """
    logger.info("On-demand weather fetch triggered for %s", city)
    
    try:
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(WeatherService.fetch_and_store_weather(city))
        
        if success:
            return {"status": "success", "city": city}
        else:
            return {"status": "failed", "city": city, "error": "API fetch failed"}
            
    except Exception as e:
        logger.error("Error in on-demand fetch: %s", e)
        return {"status": "error", "city": city, "error": str(e)}
