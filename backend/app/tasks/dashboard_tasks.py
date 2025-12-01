"""
Dashboard Data Population Tasks
Celery tasks for aggregating and populating dashboard summary data
"""

import asyncio
from .celery_app import celery_app
from .weather_tasks import DatabaseTask
from ..services.dashboard_service import DashboardService
from ..utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="app.tasks.dashboard_tasks.populate_dashboard_summary",
    base=DatabaseTask,
    bind=True,
    max_retries=2
)
def populate_dashboard_summary(self, city: str) -> dict:
    """
    Celery Task 2: Generate and store dashboard summary data
    Runs every hour
    
    This is the CRITICAL performance optimization task that:
    - Aggregates last 24 hours of raw weather data
    - Computes today's statistics (min, max, avg)
    - Generates hourly trends (24 data points)
    - Generates daily trends (7 days)
    - Calculates weather distribution
    - Stores pre-computed summary for instant dashboard loading
    
    Args:
        city: City name
        
    Returns:
        Task result dictionary
    """
    logger.info("[DASHBOARD] Starting dashboard summary population task for %s", city)
    
    try:
        # Run async service method
        loop = asyncio.get_event_loop()
        
        # Generate comprehensive dashboard summary
        summary = loop.run_until_complete(
            DashboardService.generate_dashboard_summary(city)
        )
        
        if not summary:
            logger.warning("[WARNING] No data available to generate dashboard summary for %s", city)
            return {
                "status": "no_data",
                "city": city,
                "message": "No weather data available for aggregation"
            }
        
        # Save summary to database
        success = loop.run_until_complete(
            DashboardService.save_dashboard_summary(summary)
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
        raise self.retry(exc=exc, countdown=120)  # Retry after 2 minutes


@celery_app.task(
    name="app.tasks.dashboard_tasks.generate_dashboard_on_demand",
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
        loop = asyncio.get_event_loop()
        
        summary = loop.run_until_complete(
            DashboardService.generate_dashboard_summary(city)
        )
        
        if summary:
            success = loop.run_until_complete(
                DashboardService.save_dashboard_summary(summary)
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
