"""
Weather API Routes
Endpoints for raw weather data access
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timedelta

from ...models.weather import WeatherDataResponse
from ...utils.logger import get_logger
# Legacy file - Use ../weather/weather_router.py instead
# Kept for backward compatibility only

logger = get_logger(__name__)

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get(
    "/current",
    response_model=WeatherDataResponse,
    summary="Get Current Weather",
    description="Get the most recent weather data for a city"
)
async def get_current_weather(city: Optional[str] = "Pune"):
    """
    Get the latest weather reading for a city.
    
    Args:
        city: City name
        
    Returns:
        Latest weather data
    """
    try:
        logger.info(f"Current weather requested for {city}")
        
        weather_data = await WeatherService.get_latest_weather(city)
        
        if not weather_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No weather data available for {city}"
            )
        
        # Transform to response model
        response = WeatherDataResponse(
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
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current weather"
        )


@router.get(
    "/history",
    response_model=List[WeatherDataResponse],
    summary="Get Weather History",
    description="Get historical weather data for a specified time range"
)
async def get_weather_history(
    city: Optional[str] = "Pune",
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history to retrieve (max 7 days)")
):
    """
    Get historical weather data.
    
    Args:
        city: City name
        hours: Number of hours to look back (1-168)
        
    Returns:
        List of weather readings
    """
    try:
        logger.info(f"Weather history requested for {city} (last {hours} hours)")
        
        weather_records = await WeatherService.get_weather_history(city, hours)
        
        if not weather_records:
            return []
        
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
            )
            for record in weather_records
        ]
        
        logger.info(f"Returning {len(responses)} weather records for {city}")
        return responses
        
    except Exception as e:
        logger.error(f"Error fetching weather history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weather history"
        )


@router.post(
    "/fetch",
    summary="Trigger Weather Fetch",
    description="Manually trigger weather data fetch from OpenWeatherMap API"
)
async def trigger_weather_fetch(city: Optional[str] = "Pune"):
    """
    Manually fetch fresh weather data from API.
    Useful for immediate updates or testing.
    
    Args:
        city: City name
        
    Returns:
        Fetch status
    """
    try:
        logger.info(f"Manual weather fetch triggered for {city}")
        
        success = await WeatherService.fetch_and_store_weather(city)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully fetched weather data for {city}",
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to fetch weather data from API"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering weather fetch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger weather fetch"
        )


@router.get(
    "/statistics",
    summary="Get Weather Statistics",
    description="Get aggregated weather statistics for a time range"
)
async def get_weather_statistics(
    city: Optional[str] = "Pune",
    hours: int = Query(default=24, ge=1, le=168, description="Hours to aggregate")
):
    """
    Get aggregated weather statistics.
    
    Args:
        city: City name
        hours: Number of hours to analyze
        
    Returns:
        Aggregated statistics
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        stats = await WeatherRepository.get_weather_stats(city, start_time, end_time)
        
        if not stats:
            return {
                "city": city,
                "period_hours": hours,
                "message": "No data available for the specified period"
            }
        
        return {
            "city": city,
            "period_hours": hours,
            "start_time": start_time,
            "end_time": end_time,
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
        
    except Exception as e:
        logger.error(f"Error calculating weather statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate weather statistics"
        )
