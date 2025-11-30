"""
Dashboard Data Models
Models for pre-aggregated dashboard summary data
"""

from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel, Field


class CurrentWeather(BaseModel):
    """Current weather snapshot"""
    temperature: float = Field(..., description="Current temperature")
    feels_like: float = Field(..., description="Feels like temperature")
    humidity: float = Field(..., description="Current humidity")
    pressure: int = Field(..., description="Atmospheric pressure")
    weather_main: str = Field(..., description="Weather condition")
    weather_description: str = Field(..., description="Detailed weather description")
    weather_icon: str = Field(..., description="Weather icon code")
    wind_speed: float = Field(..., description="Wind speed")
    wind_deg: int = Field(..., description="Wind direction")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Visibility")
    sunrise: datetime = Field(None, description="Sunrise time")
    sunset: datetime = Field(None, description="Sunset time")


class TodayStats(BaseModel):
    """Aggregated statistics for today"""
    temp_avg: float = Field(..., description="Average temperature")
    temp_min: float = Field(..., description="Minimum temperature")
    temp_max: float = Field(..., description="Maximum temperature")
    humidity_avg: float = Field(..., description="Average humidity")
    humidity_min: float = Field(..., description="Minimum humidity")
    humidity_max: float = Field(..., description="Maximum humidity")
    pressure_avg: int = Field(..., description="Average pressure")
    wind_speed_avg: float = Field(..., description="Average wind speed")
    records_count: int = Field(..., description="Number of records analyzed")


class HourlyTrend(BaseModel):
    """Hourly trend data point"""
    hour: datetime = Field(..., description="Hour timestamp")
    temperature: float = Field(..., description="Average temperature for the hour")
    humidity: float = Field(..., description="Average humidity for the hour")
    weather_main: str = Field(..., description="Dominant weather condition")
    wind_speed: float = Field(..., description="Average wind speed")


class DailyTrend(BaseModel):
    """Daily trend data point"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    temp_avg: float = Field(..., description="Average temperature")
    temp_min: float = Field(..., description="Minimum temperature")
    temp_max: float = Field(..., description="Maximum temperature")
    humidity_avg: float = Field(..., description="Average humidity")
    weather_main: str = Field(..., description="Dominant weather condition")
    records_count: int = Field(..., description="Number of records for the day")


class DashboardSummary(BaseModel):
    """
    Dashboard Summary Model
    Pre-aggregated data optimized for dashboard display
    """
    
    city: str = Field(..., description="City name")
    summary_type: str = Field(default="hourly", description="Summary type")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    current_weather: CurrentWeather = Field(..., description="Latest weather snapshot")
    today_stats: TodayStats = Field(..., description="Today's aggregated statistics")
    
    hourly_trend: List[HourlyTrend] = Field(
        default_factory=list,
        description="Last 24 hours trend"
    )
    daily_trend: List[DailyTrend] = Field(
        default_factory=list,
        description="Last 7 days trend"
    )
    
    weather_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Weather type distribution counts"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Pune",
                "summary_type": "hourly",
                "generated_at": "2025-11-28T10:00:00Z",
                "current_weather": {
                    "temperature": 28.5,
                    "feels_like": 30.2,
                    "humidity": 65.0,
                    "pressure": 1013,
                    "weather_main": "Clear",
                    "weather_description": "clear sky",
                    "weather_icon": "01d",
                    "wind_speed": 3.5,
                    "wind_deg": 180,
                    "clouds": 10,
                    "visibility": 10000
                },
                "today_stats": {
                    "temp_avg": 27.8,
                    "temp_min": 24.5,
                    "temp_max": 31.2,
                    "humidity_avg": 62.0,
                    "humidity_min": 45.0,
                    "humidity_max": 75.0,
                    "pressure_avg": 1012,
                    "wind_speed_avg": 3.2,
                    "records_count": 24
                },
                "hourly_trend": [
                    {
                        "hour": "2025-11-28T09:00:00Z",
                        "temperature": 27.5,
                        "humidity": 63.0,
                        "weather_main": "Clear",
                        "wind_speed": 3.0
                    }
                ],
                "daily_trend": [
                    {
                        "date": "2025-11-28",
                        "temp_avg": 27.8,
                        "temp_min": 24.5,
                        "temp_max": 31.2,
                        "humidity_avg": 62.0,
                        "weather_main": "Clear",
                        "records_count": 24
                    }
                ],
                "weather_distribution": {
                    "Clear": 15,
                    "Clouds": 7,
                    "Rain": 2
                }
            }
        }


class DashboardSummaryResponse(BaseModel):
    """API response for dashboard summary endpoint"""
    success: bool = Field(default=True)
    data: DashboardSummary
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2025-11-28T10:00:00Z",
                "data": {
                    "city": "Pune",
                    "current_weather": {
                        "temperature": 28.5,
                        "weather_main": "Clear"
                    }
                }
            }
        }
