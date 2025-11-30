"""
Script to remove weather data for all cities except Pune
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import logging
from app.config.database import DatabaseManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def cleanup_other_cities():
    """Remove all weather data except for Pune"""
    try:
        # Initialize database
        await DatabaseManager.connect()
        logger.info("Connected to database")
        
        db = DatabaseManager.get_database()
        weather_collection = db["weatherdata"]
        dashboard_collection = db["dashboardsummaries"]
        
        # Remove weather data for all cities except Pune
        result = await weather_collection.delete_many({"city": {"$ne": "Pune"}})
        logger.info(f"✓ Removed {result.deleted_count} weather records for other cities")
        
        # Remove dashboard summaries for all cities except Pune
        result = await dashboard_collection.delete_many({"city": {"$ne": "Pune"}})
        logger.info(f"✓ Removed {result.deleted_count} dashboard summaries for other cities")
        
        # Count remaining records
        pune_weather_count = await weather_collection.count_documents({"city": "Pune"})
        pune_dashboard_count = await dashboard_collection.count_documents({"city": "Pune"})
        
        logger.info(f"\nRemaining data:")
        logger.info(f"  - Pune weather records: {pune_weather_count}")
        logger.info(f"  - Pune dashboard summaries: {pune_dashboard_count}")
        
        logger.info("\n✓ Cleanup completed! Only Pune data remains.")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise
    finally:
        await DatabaseManager.disconnect()


if __name__ == "__main__":
    asyncio.run(cleanup_other_cities())
