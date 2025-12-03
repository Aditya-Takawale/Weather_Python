"""
Weather API Router
FastAPI routes for weather endpoints
"""

from fastapi import APIRouter, Query
from typing import Optional

from .weather_controller import WeatherController

router = APIRouter(prefix="/weather", tags=["Weather"])

# Initialize controller
weather_controller = WeatherController()


@router.get(
    "/current",
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
    return await weather_controller.get_current_weather(city)


@router.get(
    "/history",
    summary="Get Weather History",
    description="Get historical weather data for a specified time range"
)
async def get_weather_history(
    city: Optional[str] = "Pune",
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Hours of history to retrieve (max 7 days)"
    )
):
    """
    Get historical weather data.
    
    Args:
        city: City name
        hours: Number of hours to look back (1-168)
        
    Returns:
        List of weather readings
    """
    return await weather_controller.get_weather_history(city, hours)


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
    return await weather_controller.trigger_weather_fetch(city)


@router.get(
    "/statistics",
    summary="Get Weather Statistics",
    description="Get aggregated weather statistics for a time range"
)
async def get_weather_statistics(
    city: Optional[str] = "Pune",
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Hours to aggregate"
    )
):
    """
    Get aggregated weather statistics.
    
    Args:
        city: City name
        hours: Number of hours to analyze
        
    Returns:
        Aggregated statistics
    """
    return await weather_controller.get_weather_statistics(city, hours)
