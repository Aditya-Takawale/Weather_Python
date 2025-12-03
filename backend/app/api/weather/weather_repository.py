"""
Weather Data Repository
Database operations for raw weather data using OOP pattern
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from ...common.base_repository import BaseRepository
from ...models.weather import WeatherRaw
from ...infrastructure.config import settings


class WeatherRepository(BaseRepository[WeatherRaw]):
    """Repository for rawweatherdatas collection operations"""
    
    def __init__(self):
        """Initialize weather repository"""
        super().__init__(settings.COLLECTION_RAW_WEATHER)
    
    async def insert_weather_data(self, weather_data: WeatherRaw) -> str:
        """
        Insert raw weather data into database
        
        Args:
            weather_data: Weather data to insert
            
        Returns:
            Inserted document ID
        """
        try:
            document = weather_data.model_dump()
            result_id = await self.insert_one(document)
            
            self.logger.info(
                "Inserted weather data for %s at %s",
                weather_data.city,
                weather_data.timestamp
            )
            
            return result_id
            
        except Exception as e:
            self.logger.error("Error inserting weather data: %s", e)
            raise
    
    async def get_latest_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent weather data for a city
        
        Args:
            city: City name
            
        Returns:
            Latest weather document or None
        """
        try:
            document = await self.find_one(
                filter_dict={"city": city, "is_deleted": False},
                sort=[("timestamp", -1)]
            )
            
            return document
            
        except Exception as e:
            self.logger.error("Error fetching latest weather: %s", e)
            raise
    
    async def get_weather_by_time_range(
        self,
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
            query = {
                "city": city,
                "timestamp": {"$gte": start_time, "$lte": end_time},
                "is_deleted": False
            }
            
            documents = await self.find_many(
                filter_dict=query,
                sort=[("timestamp", -1)],
                limit=limit
            )
            
            return documents
            
        except Exception as e:
            self.logger.error("Error fetching weather by time range: %s", e)
            raise
    
    async def get_weather_last_n_hours(
        self,
        city: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
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
        
        return await self.get_weather_by_time_range(city, start_time, end_time)
    
    async def get_weather_today(self, city: str) -> List[Dict[str, Any]]:
        """
        Get all weather data for today
        
        Args:
            city: City name
            
        Returns:
            List of weather documents
        """
        today_start = datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        today_end = today_start + timedelta(days=1)
        
        return await self.get_weather_by_time_range(city, today_start, today_end)
    
    async def soft_delete_old_records(self, days: int = 2) -> int:
        """
        Soft delete weather records older than specified days
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of records marked as deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Use raw collection for update_many (not in base repository)
            collection = self._collection
            result = await collection.update_many(
                {"timestamp": {"$lt": cutoff_date}, "is_deleted": False},
                {"$set": {"is_deleted": True}}
            )
            
            count = result.modified_count
            self.logger.info(
                "Soft deleted %s weather records older than %s days",
                count,
                days
            )
            
            return count
            
        except Exception as e:
            self.logger.error("Error soft deleting old records: %s", e)
            raise
    
    async def hard_delete_old_records(self, days: int = 3) -> int:
        """
        Permanently delete weather records older than specified days
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Use delete_many from base repository
            count = await self.delete_many(
                filter_dict={"timestamp": {"$lt": cutoff_date}}
            )
            
            self.logger.info(
                "Hard deleted %s weather records older than %s days",
                count,
                days
            )
            
            return count
            
        except Exception as e:
            self.logger.error("Error hard deleting old records: %s", e)
            raise
    
    async def get_weather_stats(
        self,
        city: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
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
            
            results = await self.aggregate(pipeline)
            
            if results:
                stats = results[0]
                stats.pop("_id", None)
                return stats
            
            return {}
            
        except Exception as e:
            self.logger.error("Error calculating weather stats: %s", e)
            raise
    
    async def get_weather_distribution(
        self,
        city: str,
        hours: int = 24
    ) -> Dict[str, int]:
        """
        Get distribution of weather conditions for the last N hours
        
        Args:
            city: City name
            hours: Number of hours to analyze
            
        Returns:
            Dictionary mapping weather condition to count
        """
        try:
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
            
            results = await self.aggregate(pipeline)
            
            distribution = {item["_id"]: item["count"] for item in results}
            
            return distribution
            
        except Exception as e:
            self.logger.error("Error calculating weather distribution: %s", e)
            raise
