"""
Weather Data Repository
Database operations for raw weather data
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from ..config.database import DatabaseManager
from ..config.settings import settings
from ..models.weather import WeatherRaw
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WeatherRepository:
    """Repository for rawweatherdatas collection operations"""
    
    @classmethod
    def _get_collection(cls) -> AsyncIOMotorCollection:
        """Get raw weather data collection"""
        return DatabaseManager.get_collection(settings.COLLECTION_RAW_WEATHER)
    
    @classmethod
    async def insert_weather_data(cls, weather_data: WeatherRaw) -> str:
        """
        Insert raw weather data into database
        
        Args:
            weather_data: Weather data to insert
            
        Returns:
            Inserted document ID
        """
        try:
            collection = cls._get_collection()
            document = weather_data.model_dump()
            
            result = await collection.insert_one(document)
            logger.info(f"Inserted weather data for {weather_data.city} at {weather_data.timestamp}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error inserting weather data: {e}")
            raise
    
    @classmethod
    async def get_latest_weather(cls, city: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent weather data for a city
        
        Args:
            city: City name
            
        Returns:
            Latest weather document or None
        """
        try:
            collection = cls._get_collection()
            
            document = await collection.find_one(
                {"city": city, "is_deleted": False},
                sort=[("timestamp", -1)]
            )
            
            if document:
                document["_id"] = str(document["_id"])
            
            return document
            
        except Exception as e:
            logger.error(f"Error fetching latest weather: {e}")
            raise
    
    @classmethod
    async def get_weather_by_time_range(
        cls,
        city: str,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get weather data within a time range
        
        Args:
            city: City name
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of records
            
        Returns:
            List of weather documents
        """
        try:
            collection = cls._get_collection()
            
            query = {
                "city": city,
                "timestamp": {"$gte": start_time, "$lte": end_time},
                "is_deleted": False
            }
            
            cursor = collection.find(query).sort("timestamp", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=None)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
            
        except Exception as e:
            logger.error(f"Error fetching weather by time range: {e}")
            raise
    
    @classmethod
    async def get_weather_last_n_hours(cls, city: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get weather data for the last N hours
        
        Args:
            city: City name
            hours: Number of hours to look back
            
        Returns:
            List of weather documents
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        return await cls.get_weather_by_time_range(city, start_time, end_time)
    
    @classmethod
    async def get_weather_today(cls, city: str) -> List[Dict[str, Any]]:
        """
        Get all weather data for today
        
        Args:
            city: City name
            
        Returns:
            List of weather documents
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return await cls.get_weather_by_time_range(city, today_start, today_end)
    
    @classmethod
    async def soft_delete_old_records(cls, days: int = 2) -> int:
        """
        Soft delete weather records older than specified days
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of records marked as deleted
        """
        try:
            collection = cls._get_collection()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await collection.update_many(
                {"timestamp": {"$lt": cutoff_date}, "is_deleted": False},
                {"$set": {"is_deleted": True}}
            )
            
            count = result.modified_count
            logger.info(f"Soft deleted {count} weather records older than {days} days")
            
            return count
            
        except Exception as e:
            logger.error(f"Error soft deleting old records: {e}")
            raise
    
    @classmethod
    async def hard_delete_old_records(cls, days: int = 3) -> int:
        """
        Permanently delete weather records older than specified days
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of records deleted
        """
        try:
            collection = cls._get_collection()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await collection.delete_many(
                {"timestamp": {"$lt": cutoff_date}}
            )
            
            count = result.deleted_count
            logger.info(f"Hard deleted {count} weather records older than {days} days")
            
            return count
            
        except Exception as e:
            logger.error(f"Error hard deleting old records: {e}")
            raise
    
    @classmethod
    async def get_weather_stats(cls, city: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Get aggregated weather statistics for a time range
        
        Args:
            city: City name
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Dictionary with statistics
        """
        try:
            collection = cls._get_collection()
            
            pipeline = [
                {
                    "$match": {
                        "city": city,
                        "timestamp": {"$gte": start_time, "$lte": end_time},
                        "is_deleted": False
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "temp_avg": {"$avg": "$temperature.current"},
                        "temp_min": {"$min": "$temperature.min"},
                        "temp_max": {"$max": "$temperature.max"},
                        "humidity_avg": {"$avg": "$humidity"},
                        "humidity_min": {"$min": "$humidity"},
                        "humidity_max": {"$max": "$humidity"},
                        "pressure_avg": {"$avg": "$pressure"},
                        "wind_speed_avg": {"$avg": "$wind.speed"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                stats.pop("_id", None)
                return stats
            
            return {}
            
        except Exception as e:
            logger.error(f"Error calculating weather stats: {e}")
            raise
    
    @classmethod
    async def get_weather_distribution(cls, city: str, hours: int = 24) -> Dict[str, int]:
        """
        Get distribution of weather conditions for the last N hours
        
        Args:
            city: City name
            hours: Number of hours to analyze
            
        Returns:
            Dictionary mapping weather condition to count
        """
        try:
            collection = cls._get_collection()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            pipeline = [
                {
                    "$match": {
                        "city": city,
                        "timestamp": {"$gte": cutoff_time},
                        "is_deleted": False
                    }
                },
                {
                    "$group": {
                        "_id": "$weather.main",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            distribution = {item["_id"]: item["count"] for item in results}
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating weather distribution: {e}")
            raise
