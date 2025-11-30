"""
Script to clean the entire database except Pune data
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


async def clean_database():
    """Remove all data from database except Pune weather data"""
    try:
        # Initialize database
        await DatabaseManager.connect()
        logger.info("Connected to database")
        
        db = DatabaseManager.get_database()
        
        # Get all collections
        collections = await db.list_collection_names()
        logger.info(f"Found collections: {collections}")
        
        total_deleted = 0
        
        for collection_name in collections:
            if collection_name in ["weatherdata", "rawweatherdatas"]:
                # For weather data, keep only Pune
                collection = db[collection_name]
                result = await collection.delete_many({"city": {"$ne": "Pune"}})
                logger.info(f"✓ {collection_name}: Removed {result.deleted_count} non-Pune records")
                
                pune_count = await collection.count_documents({"city": "Pune"})
                logger.info(f"  Remaining Pune records: {pune_count}")
                total_deleted += result.deleted_count
                
            elif collection_name == "dashboardsummaries":
                # For dashboard summaries, keep only Pune
                collection = db[collection_name]
                result = await collection.delete_many({"city": {"$ne": "Pune"}})
                logger.info(f"✓ {collection_name}: Removed {result.deleted_count} non-Pune records")
                
                pune_count = await collection.count_documents({"city": "Pune"})
                logger.info(f"  Remaining Pune records: {pune_count}")
                total_deleted += result.deleted_count
                
            elif collection_name not in ["system.indexes"]:
                # For other collections, delete all records
                collection = db[collection_name]
                result = await collection.delete_many({})
                logger.info(f"✓ {collection_name}: Removed {result.deleted_count} records")
                total_deleted += result.deleted_count
        
        logger.info(f"\n✓ Database cleanup completed!")
        logger.info(f"  Total records deleted: {total_deleted}")
        logger.info(f"  Only Pune weather data remains")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise
    finally:
        await DatabaseManager.disconnect()


if __name__ == "__main__":
    asyncio.run(clean_database())
