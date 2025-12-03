"""
Weather Data Fetching Tasks
Celery tasks for fetching weather data from OpenWeatherMap API
"""

import asyncio
from celery import Task
from ....core.celery.celery_app import celery_app
from ....config.database import DatabaseManager
from ..weather_service import WeatherService
from ....core.logging.logger import get_logger

logger = get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database connection lifecycle"""
    
    _db_connected = False
    
    def run(self, *args, **kwargs):
        """Abstract run method implementation"""
    
    def before_start(self, task_id, args, kwargs):
        """Initialize database connection"""
        if not self._db_connected:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(DatabaseManager.connect())
            self._db_connected = True


@celery_app.task(
    name="api.weather.tasks.fetch_weather_data",
    base=DatabaseTask,
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def fetch_weather_data(self, city: str) -> dict:
    """
    Fetch weather data from OpenWeatherMap API and store in database.
    Scheduled to run every 30 minutes.
    
    Args:
        city: City name to fetch weather for
        
    Returns:
        Task result dictionary
    """
    logger.info("[WEATHER] Starting weather data fetch task for %s", city)
    
    try:
        # Run async service method with OOP instance
        loop = asyncio.get_event_loop()
        service = WeatherService()
        success = loop.run_until_complete(service.fetch_and_store_weather(city))
        
        if success:
            logger.info("[SUCCESS] Weather data fetch successful for %s", city)
            return {
                "status": "success",
                "city": city,
                "message": "Weather data fetched and stored successfully"
            }
        else:
            logger.error("[FAILED] Weather data fetch failed for %s", city)
            raise self.retry(exc=Exception("Failed to fetch weather data"))
            
    except Exception as exc:
        logger.error("[ERROR] Error in weather fetch task: %s", exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@celery_app.task(
    name="api.weather.tasks.fetch_weather_data_on_demand",
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
        service = WeatherService()
        success = loop.run_until_complete(service.fetch_and_store_weather(city))
        
        if success:
            return {"status": "success", "city": city}
        else:
            return {"status": "failed", "city": city, "error": "API fetch failed"}
            
    except Exception as e:
        logger.error("Error in on-demand fetch: %s", e)
        return {"status": "error", "city": city, "error": str(e)}
