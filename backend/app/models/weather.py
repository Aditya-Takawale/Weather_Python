"""
Weather Data Models
Database models for storing raw weather data
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class WeatherTemperature(BaseModel):
    """Temperature information"""
    current: float = Field(..., description="Current temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature")
    min: float = Field(..., description="Minimum temperature")
    max: float = Field(..., description="Maximum temperature")


class WeatherCondition(BaseModel):
    """Weather condition information"""
    main: str = Field(..., description="Weather condition main group")
    description: str = Field(..., description="Weather condition description")
    icon: str = Field(..., description="Weather icon code")


class WeatherWind(BaseModel):
    """Wind information"""
    speed: float = Field(..., description="Wind speed in m/s")
    deg: int = Field(..., description="Wind direction in degrees")
    gust: Optional[float] = Field(None, description="Wind gust speed")


class WeatherRaw(BaseModel):
    """
    Raw Weather Data Model
    Stores unprocessed weather data fetched from OpenWeatherMap API
    """
    
    city: str = Field(..., description="City name")
    timestamp: datetime = Field(..., description="Data timestamp")
    
    temperature: WeatherTemperature = Field(..., description="Temperature data")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    
    weather: WeatherCondition = Field(..., description="Weather condition")
    wind: WeatherWind = Field(..., description="Wind information")
    
    clouds: int = Field(..., ge=0, le=100, description="Cloudiness percentage")
    visibility: int = Field(..., description="Visibility in meters")
    
    sunrise: Optional[datetime] = Field(None, description="Sunrise time")
    sunset: Optional[datetime] = Field(None, description="Sunset time")
    
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw API response")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation time")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Pune",
                "timestamp": "2025-11-28T10:30:00Z",
                "temperature": {
                    "current": 28.5,
                    "feels_like": 30.2,
                    "min": 25.0,
                    "max": 32.0
                },
                "humidity": 65.0,
                "pressure": 1013,
                "weather": {
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                },
                "wind": {
                    "speed": 3.5,
                    "deg": 180
                },
                "clouds": 10,
                "visibility": 10000
            }
        }


class WeatherDataResponse(BaseModel):
    """API response model for weather data"""
    id: str = Field(..., description="Record ID")
    city: str
    timestamp: datetime
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float
    humidity: float
    pressure: int
    weather_main: str
    weather_description: str
    wind_speed: float
    clouds: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "city": "Pune",
                "timestamp": "2025-11-28T10:30:00Z",
                "temperature": 28.5,
                "feels_like": 30.2,
                "humidity": 65.0,
                "pressure": 1013,
                "weather_main": "Clear",
                "weather_description": "clear sky",
                "wind_speed": 3.5,
                "clouds": 10
            }
        }
