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
    
    _client: Optional[AsyncIOMotorClient] = None  # type: ignore
    _database: Optional[AsyncIOMotorDatabase] = None  # type: ignore
    
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
            logger.info("Connecting to MongoDB: %s", settings.MONGODB_URL)
            
            cls._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await cls._client.admin.command('ping')
            
            cls._database = cls._client[settings.MONGODB_DB_NAME]  # type: ignore
            
            # Create indexes
            await cls._create_indexes()
            
            logger.info("Successfully connected to MongoDB database: %s", settings.MONGODB_DB_NAME)
            
        except ConnectionFailure as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error connecting to MongoDB: %s", e)
            raise
    
    @classmethod
    async def _create_indexes(cls) -> None:
        """Create necessary indexes for optimal query performance"""
        if cls._database is None:
            return
        
        try:
            # Raw Weather Data Collection Indexes
            raw_weather = cls._database[settings.COLLECTION_RAW_WEATHER]  # type: ignore
            await raw_weather.create_index([("timestamp", -1)])
            await raw_weather.create_index([("city", 1), ("timestamp", -1)])
            await raw_weather.create_index([("is_deleted", 1)])
            await raw_weather.create_index(
                [("created_at", 1)],
                expireAfterSeconds=259200  # 3 days TTL
            )
            
            # Dashboard Summary Collection Indexes
            dashboard_summary = cls._database[settings.COLLECTION_DASHBOARD_SUMMARY]  # type: ignore
            try:
                await dashboard_summary.create_index([
                    ("city", 1),
                    ("generated_at", -1)
                ], unique=True)
            except Exception as idx_error:
                # Index might already exist or have duplicate data
                if "duplicate key" in str(idx_error).lower():
                    logger.warning("Dashboard summary has duplicate data - cleaning up")
                    # Clean up null generated_at records
                    await dashboard_summary.delete_many({"generated_at": None})
                else:
                    logger.debug("Dashboard summary index: %s", idx_error)
            
            # Alert Logs Collection Indexes
            alert_logs = cls._database[settings.COLLECTION_ALERT_LOGS]  # type: ignore
            try:
                await alert_logs.create_index([("city", 1), ("triggered_at", -1)])
                await alert_logs.create_index([("is_active", 1)])
                await alert_logs.create_index([("alert_type", 1)])
                await alert_logs.create_index([("triggered_at", -1)])
            except Exception as idx_error:
                logger.debug("Alert logs index: %s", idx_error)
            
            # Alert Configs Collection Indexes (if needed)
            alert_configs = cls._database[settings.COLLECTION_ALERT_CONFIGS]  # type: ignore
            try:
                await alert_configs.create_index([("city", 1), ("alert_type", 1)], unique=True)
            except Exception as idx_error:
                logger.debug("Alert configs index: %s", idx_error)
            
            logger.info("Database indexes verified successfully")
            
        except Exception as e:
            logger.error("Error setting up database indexes: %s", e)
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
    def get_database(cls) -> AsyncIOMotorDatabase:  # type: ignore
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
        return db[collection_name]  # type: ignore


# Convenience functions for FastAPI dependency injection
async def get_database() -> AsyncIOMotorDatabase:  # type: ignore
    """FastAPI dependency for getting database instance"""
    return DatabaseManager.get_database()


async def close_database_connection() -> None:
    """Close database connection on application shutdown"""
    await DatabaseManager.disconnect()
