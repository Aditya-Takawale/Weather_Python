"""
Dashboard Data Population Tasks
Celery tasks for aggregating and populating dashboard summary data
"""

import asyncio
from ....core.celery.celery_app import celery_app
from ....api.weather.tasks.weather_tasks import DatabaseTask
from ..dashboard_service import DashboardService
from ....core.logging.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="api.dashboard.tasks.populate_dashboard_summary",
    base=DatabaseTask,
    bind=True,
    max_retries=2
)
def populate_dashboard_summary(self, city: str) -> dict:
    """
    Generate and store dashboard summary data.
    Aggregates weather data and computes statistics for fast dashboard loading.
    Scheduled to run every hour.
    
    Args:
        city: City name
        
    Returns:
        Task result dictionary
    """
    logger.info("[DASHBOARD] Starting dashboard summary population task for %s", city)
    
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        service = DashboardService()
        
        summary = loop.run_until_complete(
            service.generate_dashboard_summary(city)
        )
        
        if not summary:
            logger.warning("[WARNING] No data available to generate dashboard summary for %s", city)
            return {
                "status": "no_data",
                "city": city,
                "message": "No weather data available for aggregation"
            }
        
        success = loop.run_until_complete(
            service.save_dashboard_summary(summary)
        )
        
        if success:
            logger.info("[SUCCESS] Dashboard summary populated successfully for %s", city)
            return {
                "status": "success",
                "city": city,
                "message": "Dashboard summary generated and stored",
                "stats": {
                    "hourly_trend_points": len(summary.hourly_trend),
                    "daily_trend_points": len(summary.daily_trend),
                    "weather_types": len(summary.weather_distribution),
                    "current_temp": summary.current_weather.temperature
                }
            }
        else:
            logger.error("[FAILED] Failed to save dashboard summary for %s", city)
            raise self.retry(exc=Exception("Failed to save dashboard summary"))
            
    except Exception as exc:
        logger.error("[ERROR] Error in dashboard population task: %s", exc)
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(
    name="api.dashboard.tasks.generate_dashboard_on_demand",
    base=DatabaseTask
)
def generate_dashboard_on_demand(city: str) -> dict:
    """
    On-demand dashboard summary generation
    Can be triggered manually or via API
    
    Args:
        city: City name
        
    Returns:
        Task result
    """
    logger.info("On-demand dashboard generation triggered for %s", city)
    
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        service = DashboardService()
        
        summary = loop.run_until_complete(
            service.generate_dashboard_summary(city)
        )
        
        if summary:
            success = loop.run_until_complete(
                service.save_dashboard_summary(summary)
            )
            
            if success:
                return {
                    "status": "success",
                    "city": city,
                    "generated_at": summary.generated_at.isoformat()
                }
        
        return {"status": "failed", "city": city}
        
    except Exception as e:
        logger.error("Error in on-demand dashboard generation: %s", e)
        return {"status": "error", "city": city, "error": str(e)}
