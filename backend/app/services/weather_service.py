"""
Weather Service
Business logic for fetching and processing weather data from OpenWeatherMap API
"""

from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from ..config.settings import settings
from ..models.weather import (
    WeatherRaw,
    WeatherTemperature,
    WeatherCondition,
    WeatherWind
)
from ..repositories.weather_repository import WeatherRepository
from ..utils.logger import get_logger
from ..utils.helpers import safe_float, safe_int

logger = get_logger(__name__)


class WeatherService:
    """Service for weather data operations"""
    
    @staticmethod
    async def fetch_weather_from_api(city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data from OpenWeatherMap API
        
        Args:
            city: City name
            
        Returns:
            Raw API response or None if failed
        """
        try:
            url = settings.openweather_url
            params = {
                "q": f"{city},{settings.OPENWEATHER_COUNTRY_CODE}",
                "appid": settings.OPENWEATHER_API_KEY,
                "units": settings.OPENWEATHER_UNITS
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info("Successfully fetched weather data for %s", city)
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error fetching weather: %s - %s", e.response.status_code, e.response.text)
            return None
        except httpx.RequestError as e:
            logger.error("Request error fetching weather: %s", e)
            return None
        except Exception as e:
            logger.error("Unexpected error fetching weather: %s", e)
            return None
    
    @staticmethod
    def transform_api_response(api_data: Dict[str, Any]) -> WeatherRaw:
        """
        Transform OpenWeatherMap API response to WeatherRaw model
        
        Args:
            api_data: Raw API response
            
        Returns:
            WeatherRaw model instance
        """
        try:
            # Extract main weather data
            main = api_data.get("main", {})
            weather_list = api_data.get("weather", [{}])
            weather_item = weather_list[0] if weather_list else {}
            wind = api_data.get("wind", {})
            sys_data = api_data.get("sys", {})
            
            # Build temperature object
            temperature = WeatherTemperature(
                current=safe_float(main.get("temp", 0)),
                feels_like=safe_float(main.get("feels_like", 0)),
                min=safe_float(main.get("temp_min", 0)),
                max=safe_float(main.get("temp_max", 0))
            )
            
            # Build weather condition object
            weather_condition = WeatherCondition(
                main=weather_item.get("main", "Unknown"),
                description=weather_item.get("description", ""),
                icon=weather_item.get("icon", "")
            )
            
            # Build wind object
            wind_data = WeatherWind(
                speed=safe_float(wind.get("speed", 0)),
                deg=safe_int(wind.get("deg", 0)),
                gust=safe_float(wind.get("gust")) if wind.get("gust") else None
            )
            
            # Convert Unix timestamps to datetime
            sunrise = None
            sunset = None
            if sys_data.get("sunrise"):
                sunrise = datetime.fromtimestamp(sys_data["sunrise"])
            if sys_data.get("sunset"):
                sunset = datetime.fromtimestamp(sys_data["sunset"])
            
            # Create WeatherRaw instance
            weather_raw = WeatherRaw(
                city=api_data.get("name", settings.OPENWEATHER_CITY),
                timestamp=datetime.fromtimestamp(api_data.get("dt", datetime.utcnow().timestamp())),
                temperature=temperature,
                humidity=safe_float(main.get("humidity", 0)),
                pressure=safe_int(main.get("pressure", 0)),
                weather=weather_condition,
                wind=wind_data,
                clouds=safe_int(api_data.get("clouds", {}).get("all", 0)),
                visibility=safe_int(api_data.get("visibility", 0)),
                sunrise=sunrise,
                sunset=sunset,
                raw_data=api_data
            )
            
            logger.debug("Transformed API response for %s", weather_raw.city)
            return weather_raw
            
        except Exception as e:
            logger.error("Error transforming API response: %s", e)
            raise
    
    @staticmethod
    async def fetch_and_store_weather(city: str) -> bool:
        """
        Fetch weather data from API and store in database
        
        Args:
            city: City name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch from API
            api_data = await WeatherService.fetch_weather_from_api(city)
            
            if not api_data:
                logger.warning("No data received from API for %s", city)
                return False
            
            # Transform to model
            weather_raw = WeatherService.transform_api_response(api_data)
            
            # Store in database
            await WeatherRepository.insert_weather_data(weather_raw)
            
            logger.info("Successfully fetched and stored weather data for %s", city)
            return True
            
        except Exception as e:
            logger.error("Error in fetch_and_store_weather: %s", e)
            return False
    
    @staticmethod
    async def get_latest_weather(city: str) -> Optional[Dict[str, Any]]:
        """
        Get latest weather data from database
        
        Args:
            city: City name
            
        Returns:
            Latest weather document or None
        """
        try:
            return await WeatherRepository.get_latest_weather(city)
        except Exception as e:
            logger.error("Error getting latest weather: %s", e)
            return None
    
    @staticmethod
    async def get_weather_history(city: str, hours: int = 24) -> list:
        """
        Get weather history for specified hours
        
        Args:
            city: City name
            hours: Number of hours to look back
            
        Returns:
            List of weather documents
        """
        try:
            return await WeatherRepository.get_weather_last_n_hours(city, hours)
        except Exception as e:
            logger.error("Error getting weather history: %s", e)
            return []
