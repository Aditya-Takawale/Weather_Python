"""
Weather Controller
HTTP request handling for weather endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import Query, status

from ...common.base_controller import BaseController
from ...common.exceptions import (
    NotFoundException,
    ServiceUnavailableException,
    BadRequestException
)
from ...models.weather import WeatherDataResponse
from .weather_service import WeatherService


class WeatherController(BaseController):
    """Controller for weather-related HTTP endpoints"""
    
    def __init__(self):
        """Initialize weather controller with service"""
        super().__init__()
        self.service = WeatherService()
    
    async def get_current_weather(
        self,
        city: Optional[str] = "Pune"
    ) -> Dict[str, Any]:
        """
        Get the latest weather reading for a city
        
        Args:
            city: City name
            
        Returns:
            Success response with current weather data
        """
        try:
            self.logger.info("Current weather requested for %s", city)
            
            weather_data = await self.service.get_latest_weather(city)
            
            # Transform to response model
            response_data = WeatherDataResponse(
                id=weather_data["_id"],
                city=weather_data["city"],
                timestamp=weather_data["timestamp"],
                temperature=weather_data["temperature"]["current"],
                feels_like=weather_data["temperature"]["feels_like"],
                humidity=weather_data["humidity"],
                pressure=weather_data["pressure"],
                weather_main=weather_data["weather"]["main"],
                weather_description=weather_data["weather"]["description"],
                wind_speed=weather_data["wind"]["speed"],
                clouds=weather_data["clouds"]
            )
            
            return self.success_response(
                data=response_data.model_dump(),
                message=f"Current weather for {city}",
                status_code=status.HTTP_200_OK
            )
            
        except NotFoundException as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_weather_history(
        self,
        city: Optional[str] = "Pune",
        hours: int = Query(
            default=24,
            ge=1,
            le=168,
            description="Hours of history (max 7 days)"
        )
    ) -> Dict[str, Any]:
        """
        Get historical weather data
        
        Args:
            city: City name
            hours: Number of hours to look back (1-168)
            
        Returns:
            Success response with weather history
        """
        try:
            self.logger.info(
                "Weather history requested for %s (last %s hours)",
                city,
                hours
            )
            
            weather_records = await self.service.get_weather_history(city, hours)
            
            if not weather_records:
                return self.success_response(
                    data=[],
                    message=f"No weather history for {city}",
                    status_code=status.HTTP_200_OK
                )
            
            # Transform to response models
            responses = [
                WeatherDataResponse(
                    id=record["_id"],
                    city=record["city"],
                    timestamp=record["timestamp"],
                    temperature=record["temperature"]["current"],
                    feels_like=record["temperature"]["feels_like"],
                    humidity=record["humidity"],
                    pressure=record["pressure"],
                    weather_main=record["weather"]["main"],
                    weather_description=record["weather"]["description"],
                    wind_speed=record["wind"]["speed"],
                    clouds=record["clouds"]
                ).model_dump()
                for record in weather_records
            ]
            
            self.logger.info("Returning %s weather records for %s", len(responses), city)
            
            return self.success_response(
                data=responses,
                message=f"Weather history for {city}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    async def trigger_weather_fetch(
        self,
        city: Optional[str] = "Pune"
    ) -> Dict[str, Any]:
        """
        Manually fetch fresh weather data from API
        
        Args:
            city: City name
            
        Returns:
            Success response with fetch status
        """
        try:
            self.logger.info("Manual weather fetch triggered for %s", city)
            
            success = await self.service.fetch_and_store_weather(city)
            
            if success:
                return self.success_response(
                    data={
                        "city": city,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    message=f"Successfully fetched weather data for {city}",
                    status_code=status.HTTP_200_OK
                )
            else:
                raise ServiceUnavailableException(
                    message="Failed to fetch weather data from API",
                    details={"city": city}
                )
            
        except ServiceUnavailableException as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_weather_statistics(
        self,
        city: Optional[str] = "Pune",
        hours: int = Query(
            default=24,
            ge=1,
            le=168,
            description="Hours to aggregate"
        )
    ) -> Dict[str, Any]:
        """
        Get aggregated weather statistics
        
        Args:
            city: City name
            hours: Number of hours to analyze
            
        Returns:
            Success response with aggregated statistics
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            stats = await self.service.repository.get_weather_stats(
                city,
                start_time,
                end_time
            )
            
            if not stats:
                return self.success_response(
                    data={
                        "city": city,
                        "period_hours": hours,
                        "message": "No data available for the specified period"
                    },
                    message="No statistics available",
                    status_code=status.HTTP_200_OK
                )
            
            statistics_data = {
                "city": city,
                "period_hours": hours,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "statistics": {
                    "temperature": {
                        "average": round(stats.get("temp_avg", 0), 1),
                        "minimum": round(stats.get("temp_min", 0), 1),
                        "maximum": round(stats.get("temp_max", 0), 1)
                    },
                    "humidity": {
                        "average": round(stats.get("humidity_avg", 0), 1),
                        "minimum": round(stats.get("humidity_min", 0), 1),
                        "maximum": round(stats.get("humidity_max", 0), 1)
                    },
                    "pressure": {
                        "average": int(stats.get("pressure_avg", 0))
                    },
                    "wind_speed": {
                        "average": round(stats.get("wind_speed_avg", 0), 1)
                    },
                    "records_analyzed": stats.get("count", 0)
                }
            }
            
            return self.success_response(
                data=statistics_data,
                message=f"Weather statistics for {city}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
