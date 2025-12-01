"""
Weather Alert Tasks
Celery tasks for checking weather conditions and triggering alerts
"""

import asyncio
from .celery_app import celery_app
from .weather_tasks import DatabaseTask
from ..services.alert_service import AlertService
from ..utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="app.tasks.alert_tasks.check_weather_alerts",
    base=DatabaseTask,
    bind=True,
    max_retries=2
)
def check_weather_alerts(self, city: str) -> dict:
    """
    Celery Task 4: Check weather conditions and create alerts
    Runs every 15 minutes
    
    Monitors weather conditions against defined thresholds:
    - High temperature (> 35°C)
    - Low temperature (< 5°C)
    - High humidity (> 80%)
    - Extreme weather (Storm, Thunderstorm, etc.)
    
    Creates alert logs and sends notifications when thresholds are exceeded.
    Implements cooldown period to prevent duplicate alerts.
    
    Args:
        city: City name
        
    Returns:
        Task result dictionary
    """
    logger.info("[ALERT] Starting weather alert check task for %s", city)
    
    try:
        # Run async service method
        loop = asyncio.get_event_loop()
        
        # Check all alert conditions
        alert_ids = loop.run_until_complete(
            AlertService.check_and_create_alerts(city)
        )
        
        if alert_ids:
            logger.warning("[WARNING] %s weather alert(s) triggered for %s", len(alert_ids), city)
            return {
                "status": "alerts_triggered",
                "city": city,
                "alert_count": len(alert_ids),
                "alert_ids": alert_ids,
                "message": f"Created {len(alert_ids)} weather alert(s)"
            }
        else:
            logger.info("[SUCCESS] No alerts triggered for %s (conditions normal)", city)
            return {
                "status": "no_alerts",
                "city": city,
                "message": "Weather conditions within normal thresholds"
            }
            
    except Exception as exc:
        logger.error("[ERROR] Error in weather alert check task: %s", exc)
        raise self.retry(exc=exc, countdown=60)  # Retry after 1 minute


@celery_app.task(
    name="app.tasks.alert_tasks.check_alerts_on_demand",
    base=DatabaseTask
)
def check_alerts_on_demand(city: str) -> dict:
    """
    On-demand alert check
    Can be triggered manually via API
    
    Args:
        city: City name
        
    Returns:
        Task result
    """
    logger.info("On-demand alert check triggered for %s", city)
    
    try:
        loop = asyncio.get_event_loop()
        
        alert_ids = loop.run_until_complete(
            AlertService.check_and_create_alerts(city)
        )
        
        return {
            "status": "success",
            "city": city,
            "alert_count": len(alert_ids),
            "alert_ids": alert_ids
        }
        
    except Exception as e:
        logger.error("Error in on-demand alert check: %s", e)
        return {"status": "error", "city": city, "error": str(e)}


@celery_app.task(
    name="app.tasks.alert_tasks.send_alert_digest",
    base=DatabaseTask
)
def send_alert_digest(city: str, hours: int = 24) -> dict:
    """
    Send a digest of recent alerts
    Can be scheduled daily or triggered manually
    
    Args:
        city: City name
        hours: Hours to include in digest
        
    Returns:
        Task result
    """
    logger.info("[DIGEST] Generating alert digest for %s (last %s hours)", city, hours)
    
    try:
        loop = asyncio.get_event_loop()
        
        # Get recent alerts
        recent_alerts = loop.run_until_complete(
            AlertService.get_recent_alerts(city, hours)
        )
        
        # Get alert statistics
        stats = loop.run_until_complete(
            AlertService.get_alert_stats(city)
        )
        
        if recent_alerts:
            logger.info("Alert digest: %s alerts in last %s hours", len(recent_alerts), hours)
            
            # NOTE: Email digest formatting can be implemented here
            # For now, just log summary
            digest_summary = {
                "city": city,
                "period_hours": hours,
                "total_alerts": len(recent_alerts),
                "active_alerts": stats.get("active_alerts", 0),
                "by_severity": stats.get("by_severity", {}),
                "by_type": stats.get("by_type", {})
            }
            
            logger.info("Alert digest summary: %s", digest_summary)
            
            return {
                "status": "success",
                "city": city,
                "digest": digest_summary
            }
        else:
            logger.info("No alerts to report for %s", city)
            return {
                "status": "no_alerts",
                "city": city,
                "message": "No alerts in the specified period"
            }
            
    except Exception as e:
        logger.error("Error generating alert digest: %s", e)
        return {"status": "error", "city": city, "error": str(e)}
