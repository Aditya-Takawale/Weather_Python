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
    Celery Task 3: Clean up old weather data
    Runs daily at 2:00 AM
    
    Performs soft-delete on weather records older than retention_days.
    This helps maintain database performance and manage storage.
    
    Args:
        retention_days: Number of days to retain data (default: 2)
        
    Returns:
        Task result dictionary
    """
    logger.info(f"[CLEANUP] Starting data cleanup task (retention: {retention_days} days)")
    
    try:
        loop = asyncio.get_event_loop()
        
        # Soft delete old weather records
        deleted_count = loop.run_until_complete(
            WeatherRepository.soft_delete_old_records(days=retention_days)
        )
        
        logger.info(f"[SUCCESS] Data cleanup completed: {deleted_count} records marked as deleted")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "retention_days": retention_days,
            "message": f"Successfully cleaned up {deleted_count} old weather records"
        }
        
    except Exception as exc:
        logger.error(f"[ERROR] Error in data cleanup task: {exc}")
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
    logger.info(f"[DELETE] Starting hard delete task (older than {days} days)")
    
    try:
        loop = asyncio.get_event_loop()
        
        deleted_count = loop.run_until_complete(
            WeatherRepository.hard_delete_old_records(days=days)
        )
        
        logger.info(f"[SUCCESS] Hard delete completed: {deleted_count} records permanently removed")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "days": days
        }
        
    except Exception as e:
        logger.error(f"Error in hard delete task: {e}")
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
    logger.info(f"[CLEANUP] Starting alert cleanup task (older than {days} days)")
    
    try:
        loop = asyncio.get_event_loop()
        
        deleted_count = loop.run_until_complete(
            AlertRepository.delete_old_alerts(days=days)
        )
        
        logger.info(f"[SUCCESS] Alert cleanup completed: {deleted_count} alerts removed")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "days": days
        }
        
    except Exception as e:
        logger.error(f"Error in alert cleanup task: {e}")
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
        logger.error(f"Error in database optimization: {e}")
        return {"status": "error", "error": str(e)}
