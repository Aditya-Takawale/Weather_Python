"""
Application Settings and Configuration Management
Centralized configuration using Pydantic Settings
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables"""
    
    # Application Settings
    APP_NAME: str = "Weather Monitoring System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Server Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")
    API_RELOAD: bool = Field(default=True, description="Auto-reload on code changes")
    
    # MongoDB Configuration
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL"
    )
    MONGODB_DB_NAME: str = Field(
        default="weather_dashboard",
        description="MongoDB database name"
    )
    MONGODB_MAX_POOL_SIZE: int = Field(default=10, description="MongoDB connection pool size")
    MONGODB_MIN_POOL_SIZE: int = Field(default=1, description="MongoDB minimum pool size")
    
    # Redis Configuration (Celery Broker)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery"
    )
    
    # OpenWeatherMap API Configuration
    OPENWEATHER_API_KEY: str = Field(
        default="b369be1b643c9bc1422d0e5d157aa3a8",
        description="OpenWeatherMap API key"
    )
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_CITY: str = Field(default="Pune", description="City to monitor")
    OPENWEATHER_COUNTRY_CODE: str = Field(default="IN", description="Country code")
    OPENWEATHER_UNITS: str = Field(default="metric", description="Temperature units")
    
    # Alert Thresholds
    ALERT_TEMP_HIGH: float = Field(default=35.0, description="High temperature threshold (°C)")
    ALERT_TEMP_LOW: float = Field(default=5.0, description="Low temperature threshold (°C)")
    ALERT_HUMIDITY_HIGH: float = Field(default=80.0, description="High humidity threshold (%)")
    ALERT_EXTREME_WEATHER: List[str] = Field(
        default=["Storm", "Thunderstorm", "Tornado", "Hurricane"],
        description="Extreme weather conditions to alert on"
    )
    
    # MongoDB Collection Names
    COLLECTION_RAW_WEATHER: str = "rawweatherdatas"
    COLLECTION_DASHBOARD_SUMMARY: str = "dashboardsummaries"
    COLLECTION_ALERT_LOGS: str = "alertlogs"
    COLLECTION_ALERT_CONFIGS: str = "alertconfigs"
    
    # Data Retention
    DATA_RETENTION_DAYS: int = Field(default=2, description="Days to keep raw weather data")
    ALERT_COOLDOWN_MINUTES: int = Field(
        default=60,
        description="Minutes to wait before sending duplicate alert"
    )
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def openweather_url(self) -> str:
        """Get OpenWeatherMap API URL for current weather"""
        return f"{self.OPENWEATHER_BASE_URL}/weather"
    
    @property
    def mongodb_connection_string(self) -> str:
        """Get formatted MongoDB connection string"""
        return self.MONGODB_URL


# Global settings instance
settings = Settings()
