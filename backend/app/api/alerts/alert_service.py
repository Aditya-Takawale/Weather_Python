"""
Alert Service
Business logic for weather alert detection and notification using OOP pattern
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ...common.base_service import BaseService
from ...common.exceptions import NotFoundException, InternalServerException
from ...common.decorators import log_execution, handle_exceptions
from ...config.settings import settings
from ...models.alert import (
    AlertLog,
    AlertType,
    AlertSeverity,
    AlertCondition
)
from ...core.utils import safe_float
from ..weather.weather_repository import WeatherRepository
from .alert_repository import AlertRepository


class AlertService(BaseService[AlertLog]):
    """Service for weather alert detection and management"""
    
    # Alert thresholds
    HIGH_TEMP_THRESHOLD = 35.0  # °C
    LOW_TEMP_THRESHOLD = 10.0   # °C
    HIGH_HUMIDITY_THRESHOLD = 85.0  # %
    EXTREME_WEATHER_TYPES = ["Thunderstorm", "Tornado", "Hurricane", "Blizzard"]
    
    def __init__(self):
        """Initialize alert service with repositories"""
        super().__init__()
        self.repository = AlertRepository()
        self.weather_repository = WeatherRepository()
    
    @log_execution
    @handle_exceptions
    async def check_and_create_alerts(self, city: str) -> List[str]:
        """
        Check latest weather data against thresholds and create alerts
        
        Args:
            city: City name
            
        Returns:
            List of created alert IDs
        """
        try:
            self._log_info("Checking weather alerts for %s", city)
            
            # Get latest weather data
            latest_weather = await self.weather_repository.get_latest_weather(city)
            
            if not latest_weather:
                self._log_warning("No weather data available for alert checking: %s", city)
                return []
            
            created_alert_ids = []
            
            # Check high temperature
            alert_id = await self._check_high_temperature(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            # Check low temperature
            alert_id = await self._check_low_temperature(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            # Check high humidity
            alert_id = await self._check_high_humidity(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            # Check extreme weather
            alert_id = await self._check_extreme_weather(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            if created_alert_ids:
                self._log_info("Created %s alerts for %s", len(created_alert_ids), city)
            else:
                self._log_info("No alerts triggered for %s", city)
            
            return created_alert_ids
            
        except Exception as e:
            self._log_error("Error checking alerts: %s", e)
            return []
    
    async def _check_high_temperature(
        self,
        city: str,
        weather_data: Dict[str, Any]
    ) -> Optional[str]:
        """Check for high temperature alert"""
        try:
            temp = safe_float(weather_data.get("temperature", {}).get("current", 0))
            
            if temp >= self.HIGH_TEMP_THRESHOLD:
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.HIGH_TEMPERATURE,
                    severity=AlertSeverity.WARNING,
                    message=f"High temperature alert: {temp}°C",
                    triggered_at=datetime.utcnow(),
                    condition=AlertCondition(
                        metric="temperature",
                        threshold=self.HIGH_TEMP_THRESHOLD,
                        actual_value=temp,
                        operator="greater_than"
                    ),
                    metadata={
                        "feels_like": safe_float(weather_data.get("temperature", {}).get("feels_like", 0)),
                        "humidity": safe_float(weather_data.get("humidity", 0))
                    }
                )
                
                return await self.repository.insert_alert(alert)
            
            return None
            
        except Exception as e:
            self._log_error("Error checking high temperature: %s", e)
            return None
    
    async def _check_low_temperature(
        self,
        city: str,
        weather_data: Dict[str, Any]
    ) -> Optional[str]:
        """Check for low temperature alert"""
        try:
            temp = safe_float(weather_data.get("temperature", {}).get("current", 0))
            
            if temp <= self.LOW_TEMP_THRESHOLD:
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.LOW_TEMPERATURE,
                    severity=AlertSeverity.INFO,
                    message=f"Low temperature alert: {temp}°C",
                    triggered_at=datetime.utcnow(),
                    condition=AlertCondition(
                        metric="temperature",
                        threshold=self.LOW_TEMP_THRESHOLD,
                        actual_value=temp,
                        operator="less_than"
                    ),
                    metadata={
                        "feels_like": safe_float(weather_data.get("temperature", {}).get("feels_like", 0)),
                        "wind_speed": safe_float(weather_data.get("wind", {}).get("speed", 0))
                    }
                )
                
                return await self.repository.insert_alert(alert)
            
            return None
            
        except Exception as e:
            self._log_error("Error checking low temperature: %s", e)
            return None
    
    async def _check_high_humidity(
        self,
        city: str,
        weather_data: Dict[str, Any]
    ) -> Optional[str]:
        """Check for high humidity alert"""
        try:
            humidity = safe_float(weather_data.get("humidity", 0))
            
            if humidity >= self.HIGH_HUMIDITY_THRESHOLD:
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.HIGH_HUMIDITY,
                    severity=AlertSeverity.INFO,
                    message=f"High humidity alert: {humidity}%",
                    triggered_at=datetime.utcnow(),
                    condition=AlertCondition(
                        metric="humidity",
                        threshold=self.HIGH_HUMIDITY_THRESHOLD,
                        actual_value=humidity,
                        operator="greater_than"
                    ),
                    metadata={
                        "temperature": safe_float(weather_data.get("temperature", {}).get("current", 0)),
                        "feels_like": safe_float(weather_data.get("temperature", {}).get("feels_like", 0))
                    }
                )
                
                return await self.repository.insert_alert(alert)
            
            return None
            
        except Exception as e:
            self._log_error("Error checking high humidity: %s", e)
            return None
    
    async def _check_extreme_weather(
        self,
        city: str,
        weather_data: Dict[str, Any]
    ) -> Optional[str]:
        """Check for extreme weather alert"""
        try:
            weather_main = weather_data.get("weather", {}).get("main", "")
            
            if weather_main in self.EXTREME_WEATHER_TYPES:
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.EXTREME_WEATHER,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Extreme weather alert: {weather_main}",
                    triggered_at=datetime.utcnow(),
                    condition=AlertCondition(
                        metric="weather_condition",
                        threshold=0,
                        actual_value=0,
                        operator="equals",
                        description=weather_main
                    ),
                    metadata={
                        "weather_description": weather_data.get("weather", {}).get("description", ""),
                        "temperature": safe_float(weather_data.get("temperature", {}).get("current", 0)),
                        "wind_speed": safe_float(weather_data.get("wind", {}).get("speed", 0))
                    }
                )
                
                return await self.repository.insert_alert(alert)
            
            return None
            
        except Exception as e:
            self._log_error("Error checking extreme weather: %s", e)
            return None
    
    @log_execution
    @handle_exceptions
    async def get_active_alerts(
        self,
        city: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get active (unacknowledged) alerts
        
        Args:
            city: Optional city filter
            limit: Maximum number of alerts
            
        Returns:
            List of active alerts
        """
        return await self.repository.get_active_alerts(city, limit)
    
    @log_execution
    @handle_exceptions
    async def get_recent_alerts(
        self,
        city: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts within specified hours
        
        Args:
            city: Optional city filter
            hours: Number of hours to look back
            limit: Maximum number of alerts
            
        Returns:
            List of recent alerts
        """
        return await self.repository.get_recent_alerts(city, hours, limit)
    
    @log_execution
    @handle_exceptions
    async def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """
        Mark alert as acknowledged
        
        Args:
            alert_id: Alert ID
            user: User who acknowledged
            
        Returns:
            True if successful
        """
        success = await self.repository.acknowledge_alert(alert_id, user)
        
        if not success:
            raise NotFoundException(
                message=f"Alert not found: {alert_id}",
                details={"alert_id": alert_id}
            )
        
        return success
    
    @log_execution
    @handle_exceptions
    async def get_alert_stats(
        self,
        city: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get alert statistics
        
        Args:
            city: Optional city filter
            hours: Number of hours to analyze
            
        Returns:
            Alert statistics
        """
        return await self.repository.get_alert_stats(city, hours)
