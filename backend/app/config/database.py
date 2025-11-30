"""
MongoDB Database Connection and Management
Provides singleton database connection with proper lifecycle management
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging

from .settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton MongoDB connection manager"""
    
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls) -> None:
        """
        Establish MongoDB connection
        Creates indexes on collections for optimal query performance
        """
        if cls._client is not None:
            logger.warning("Database already connected")
            return
        
        try:
            logger.info(f"Connecting to MongoDB: {settings.MONGODB_URL}")
            
            cls._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await cls._client.admin.command('ping')
            
            cls._database = cls._client[settings.MONGODB_DB_NAME]
            
            # Create indexes
            await cls._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    @classmethod
    async def _create_indexes(cls) -> None:
        """Create necessary indexes for optimal query performance"""
        if cls._database is None:
            return
        
        try:
            # Raw Weather Data Collection Indexes
            raw_weather = cls._database[settings.COLLECTION_RAW_WEATHER]
            await raw_weather.create_index([("timestamp", -1)])
            await raw_weather.create_index([("city", 1), ("timestamp", -1)])
            await raw_weather.create_index([("is_deleted", 1)])
            await raw_weather.create_index(
                [("created_at", 1)],
                expireAfterSeconds=259200  # 3 days TTL
            )
            
            # Dashboard Summary Collection Indexes
            dashboard_summary = cls._database[settings.COLLECTION_DASHBOARD_SUMMARY]
            await dashboard_summary.create_index([
                ("city", 1),
                ("generated_at", -1)
            ], unique=True)
            
            # Alert Logs Collection Indexes
            alert_logs = cls._database[settings.COLLECTION_ALERT_LOGS]
            await alert_logs.create_index([("city", 1), ("triggered_at", -1)])
            await alert_logs.create_index([("is_active", 1)])
            await alert_logs.create_index([("alert_type", 1)])
            await alert_logs.create_index([("triggered_at", -1)])
            
            # Alert Configs Collection Indexes (if needed)
            alert_configs = cls._database[settings.COLLECTION_ALERT_CONFIGS]
            await alert_configs.create_index([("city", 1), ("alert_type", 1)], unique=True)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            # Don't raise - indexes are optimization, not critical
    
    @classmethod
    async def disconnect(cls) -> None:
        """Close MongoDB connection"""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._database = None
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """
        Get database instance
        
        Returns:
            AsyncIOMotorDatabase: MongoDB database instance
            
        Raises:
            RuntimeError: If database is not connected
        """
        if cls._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls._database
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Get collection instance
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection instance
        """
        db = cls.get_database()
        return db[collection_name]


# Convenience functions for FastAPI dependency injection
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency for getting database instance"""
    return DatabaseManager.get_database()


async def close_database_connection() -> None:
    """Close database connection on application shutdown"""
    await DatabaseManager.disconnect()
