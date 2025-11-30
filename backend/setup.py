"""
Setup script for Weather Monitoring System backend
Run this script to initialize the database and create indexes
"""

import asyncio
from app.config.database import DatabaseManager
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def setup_database():
    """Initialize database and create indexes"""
    logger.info("Starting database setup...")
    
    try:
        # Initialize database connection
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        logger.info("Database connection established")
        logger.info("Indexes created successfully")
        logger.info(f"Database: {settings.MONGODB_DB_NAME}")
        logger.info("Collections: weather_raw, dashboard_summary, alert_logs")
        logger.info("✓ Database setup complete!")
        
        # Close connection
        await db_manager.close()
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Weather Monitoring System - Database Setup")
    print("=" * 60)
    asyncio.run(setup_database())
