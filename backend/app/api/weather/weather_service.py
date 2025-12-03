"""
Weather Service
Business logic for fetching and processing weather data from OpenWeatherMap API
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import httpx

from ...common.base_service import BaseService
from ...common.exceptions import (
    ServiceUnavailableException,
    NotFoundException,
    InternalServerException
)
from ...common.decorators import log_execution, handle_exceptions
from ...infrastructure.config import settings
from ...models.weather import (
    WeatherRaw,
    WeatherTemperature,
    WeatherCondition,
    WeatherWind
)
from ...core.utils import safe_float, safe_int
from .weather_repository import WeatherRepository


class WeatherService(BaseService[WeatherRaw]):
    """Service for weather data operations"""
    
    def __init__(self):
        """Initialize weather service with repository"""
        super().__init__()
        self.repository = WeatherRepository()
    
    @log_execution
    @handle_exceptions
    async def fetch_weather_from_api(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data from OpenWeatherMap API
        
        Args:
            city: City name
            
        Returns:
            Raw API response or None if failed
            
        Raises:
            ServiceUnavailableException: If API is unavailable
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
                self._log_info("Successfully fetched weather data for %s", city)
                return data
                
        except httpx.HTTPStatusError as e:
            self._log_error(
                "HTTP error fetching weather: %s - %s",
                e.response.status_code,
                e.response.text
            )
            raise ServiceUnavailableException(
                message=f"Weather API returned error: {e.response.status_code}",
                details={"city": city, "status_code": e.response.status_code}
            )
            
        except httpx.RequestError as e:
            self._log_error("Request error fetching weather: %s", e)
            raise ServiceUnavailableException(
                message="Failed to connect to weather API",
                details={"city": city, "error": str(e)}
            )
            
        except Exception as e:
            self._log_error("Unexpected error fetching weather: %s", e)
            raise InternalServerException(
                message="Unexpected error fetching weather data",
                details={"city": city, "error": str(e)}
            )
    
    def transform_api_response(self, api_data: Dict[str, Any]) -> WeatherRaw:
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
                timestamp=datetime.fromtimestamp(
                    api_data.get("dt", datetime.utcnow().timestamp())
                ),
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
            
            self._log_info("Transformed API response for %s", weather_raw.city)
            return weather_raw
            
        except Exception as e:
            self._log_error("Error transforming API response: %s", e)
            raise InternalServerException(
                message="Failed to transform weather data",
                details={"error": str(e)}
            )
    
    @log_execution
    @handle_exceptions
    async def fetch_and_store_weather(self, city: str) -> bool:
        """
        Fetch weather data from API and store in database
        
        Args:
            city: City name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch from API
            api_data = await self.fetch_weather_from_api(city)
            
            if not api_data:
                self._log_warning("No data received from API for %s", city)
                return False
            
            # Transform to model
            weather_raw = self.transform_api_response(api_data)
            
            # Store in database
            await self.repository.insert_weather_data(weather_raw)
            
            self._log_info(
                "Successfully fetched and stored weather data for %s",
                city
            )
            return True
            
        except Exception as e:
            self._log_error("Error in fetch_and_store_weather: %s", e)
            return False
    
    @log_execution
    @handle_exceptions
    async def get_latest_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Get latest weather data from database
        
        Args:
            city: City name
            
        Returns:
            Latest weather document or None
            
        Raises:
            NotFoundException: If no weather data found
        """
        try:
            weather_data = await self.repository.get_latest_weather(city)
            
            if not weather_data:
                raise NotFoundException(
                    message=f"No weather data found for city: {city}",
                    details={"city": city}
                )
            
            return weather_data
            
        except NotFoundException:
            raise
        except Exception as e:
            self._log_error("Error getting latest weather: %s", e)
            raise InternalServerException(
                message="Failed to retrieve weather data",
                details={"city": city, "error": str(e)}
            )
    
    @log_execution
    @handle_exceptions
    async def get_weather_history(
        self,
        city: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get weather history for specified hours
        
        Args:
            city: City name
            hours: Number of hours to look back
            
        Returns:
            List of weather documents
        """
        try:
            history = await self.repository.get_weather_last_n_hours(city, hours)
            return history
            
        except Exception as e:
            self._log_error("Error getting weather history: %s", e)
            raise InternalServerException(
                message="Failed to retrieve weather history",
                details={"city": city, "hours": hours, "error": str(e)}
            )
