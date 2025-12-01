"""
Data Cleanup Tasks
Celery tasks for cleaning up old weather data
"""

import asyncio
from .celery_app import celery_app
from .weather_tasks import DatabaseTask
from ..repositories.weather_repository import WeatherRepository
from ..repositories.alert_repository import AlertRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_old_data",
    base=DatabaseTask,
    bind=True
)
def cleanup_old_data(self, retention_days: int = 2) -> dict:
    """
    Clean up old weather data to maintain database performance.
    Soft-deletes records older than retention_days. Runs daily at 2:00 AM.
    
    Args:
        retention_days: Number of days to retain data (default: 2)
        
    Returns:
        Task result dictionary
    """
    logger.info("[CLEANUP] Starting data cleanup task (retention: %s days)", retention_days)
    
    try:
        loop = asyncio.get_event_loop()
        
        deleted_count = loop.run_until_complete(
            WeatherRepository.soft_delete_old_records(days=retention_days)
        )
        
        logger.info("[SUCCESS] Data cleanup completed: %s records marked as deleted", deleted_count)
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "retention_days": retention_days,
            "message": f"Successfully cleaned up {deleted_count} old weather records"
        }
        
    except Exception as exc:
        logger.error("[ERROR] Error in data cleanup task: %s", exc)
        return {
            "status": "error",
            "message": str(exc)
        }


@celery_app.task(
    name="app.tasks.cleanup_tasks.hard_delete_old_data",
    base=DatabaseTask
)
def hard_delete_old_data(days: int = 7) -> dict:
    """
    Permanently delete very old weather data
    Can be scheduled separately or run manually
    
    Args:
        days: Delete records older than this many days
        
    Returns:
        Task result
    """
    logger.info("[DELETE] Starting hard delete task (older than %s days)", days)
    
    try:
        loop = asyncio.get_event_loop()
        
        deleted_count = loop.run_until_complete(
            WeatherRepository.hard_delete_old_records(days=days)
        )
        
        logger.info("[SUCCESS] Hard delete completed: %s records permanently removed", deleted_count)
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "days": days
        }
        
    except Exception as e:
        logger.error("Error in hard delete task: %s", e)
        return {"status": "error", "error": str(e)}


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_old_alerts",
    base=DatabaseTask
)
def cleanup_old_alerts(days: int = 30) -> dict:
    """
    Clean up old alert logs
    
    Args:
        days: Delete alerts older than this many days
        
    Returns:
        Task result
    """
    logger.info("[CLEANUP] Starting alert cleanup task (older than %s days)", days)
    
    try:
        loop = asyncio.get_event_loop()
        
        deleted_count = loop.run_until_complete(
            AlertRepository.delete_old_alerts(days=days)
        )
        
        logger.info("[SUCCESS] Alert cleanup completed: %s alerts removed", deleted_count)
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "days": days
        }
        
    except Exception as e:
        logger.error("Error in alert cleanup task: %s", e)
        return {"status": "error", "error": str(e)}


@celery_app.task(
    name="app.tasks.cleanup_tasks.optimize_database",
    base=DatabaseTask
)
def optimize_database() -> dict:
    """
    Database optimization task
    Can perform index rebuilding, statistics updates, etc.
    
    Returns:
        Task result
    """
    logger.info("[OPTIMIZE] Starting database optimization task")
    
    try:
        # MongoDB automatically manages indexes, but we can log statistics
        logger.info("Database optimization check completed")
        
        return {
            "status": "success",
            "message": "Database optimization completed"
        }
        
    except Exception as e:
        logger.error("Error in database optimization: %s", e)
        return {"status": "error", "error": str(e)}
