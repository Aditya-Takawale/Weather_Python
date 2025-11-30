"""
Alert Service
Business logic for weather alert detection and notification
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ..config.settings import settings
from ..models.alert import (
    AlertLog,
    AlertType,
    AlertSeverity,
    AlertCondition
)
from ..repositories.weather_repository import WeatherRepository
from ..repositories.alert_repository import AlertRepository
from ..utils.logger import get_logger
from ..utils.helpers import safe_float

logger = get_logger(__name__)


class AlertService:
    """Service for weather alert detection and management"""
    
    @staticmethod
    async def check_and_create_alerts(city: str) -> List[str]:
        """
        Check latest weather data against thresholds and create alerts
        
        Args:
            city: City name
            
        Returns:
            List of created alert IDs
        """
        try:
            logger.info(f"Checking weather alerts for {city}")
            
            # Get latest weather data
            latest_weather = await WeatherRepository.get_latest_weather(city)
            
            if not latest_weather:
                logger.warning(f"No weather data available for alert checking: {city}")
                return []
            
            created_alert_ids = []
            
            # Check high temperature
            alert_id = await AlertService._check_high_temperature(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            # Check low temperature
            alert_id = await AlertService._check_low_temperature(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            # Check high humidity
            alert_id = await AlertService._check_high_humidity(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            # Check extreme weather
            alert_id = await AlertService._check_extreme_weather(city, latest_weather)
            if alert_id:
                created_alert_ids.append(alert_id)
            
            if created_alert_ids:
                logger.info(f"Created {len(created_alert_ids)} alerts for {city}")
            else:
                logger.debug(f"No alerts triggered for {city}")
            
            return created_alert_ids
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    @staticmethod
    async def _check_high_temperature(city: str, weather_data: Dict[str, Any]) -> Optional[str]:
        """Check for high temperature alert"""
        try:
            temp_current = safe_float(weather_data.get("temperature", {}).get("current", 0))
            threshold = settings.ALERT_TEMP_HIGH
            
            if temp_current > threshold:
                # Check cooldown period
                recent_alert = await AlertRepository.check_recent_similar_alert(
                    city,
                    AlertType.HIGH_TEMPERATURE,
                    minutes=settings.ALERT_COOLDOWN_MINUTES
                )
                
                if recent_alert:
                    logger.debug(f"High temperature alert in cooldown period for {city}")
                    return None
                
                # Create alert
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.HIGH_TEMPERATURE,
                    severity=AlertSeverity.WARNING if temp_current < threshold + 5 else AlertSeverity.CRITICAL,
                    message=f"High temperature alert: {temp_current}°C (threshold: {threshold}°C)",
                    condition=AlertCondition(
                        threshold_type="temperature",
                        threshold_value=threshold,
                        actual_value=temp_current,
                        operator=">",
                        unit="°C"
                    ),
                    metadata={
                        "temperature": temp_current,
                        "humidity": weather_data.get("humidity"),
                        "weather_main": weather_data.get("weather", {}).get("main")
                    }
                )
                
                alert_id = await AlertRepository.insert_alert(alert)
                logger.warning(f"HIGH TEMPERATURE ALERT: {city} - {temp_current}°C")
                
                # Send notification (console for now)
                await AlertService._send_notification(alert)
                
                return alert_id
                
        except Exception as e:
            logger.error(f"Error checking high temperature: {e}")
        
        return None
    
    @staticmethod
    async def _check_low_temperature(city: str, weather_data: Dict[str, Any]) -> Optional[str]:
        """Check for low temperature alert"""
        try:
            temp_current = safe_float(weather_data.get("temperature", {}).get("current", 0))
            threshold = settings.ALERT_TEMP_LOW
            
            if temp_current < threshold:
                # Check cooldown period
                recent_alert = await AlertRepository.check_recent_similar_alert(
                    city,
                    AlertType.LOW_TEMPERATURE,
                    minutes=settings.ALERT_COOLDOWN_MINUTES
                )
                
                if recent_alert:
                    return None
                
                # Create alert
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.LOW_TEMPERATURE,
                    severity=AlertSeverity.WARNING if temp_current > threshold - 5 else AlertSeverity.CRITICAL,
                    message=f"Low temperature alert: {temp_current}°C (threshold: {threshold}°C)",
                    condition=AlertCondition(
                        threshold_type="temperature",
                        threshold_value=threshold,
                        actual_value=temp_current,
                        operator="<",
                        unit="°C"
                    ),
                    metadata={
                        "temperature": temp_current,
                        "humidity": weather_data.get("humidity"),
                        "weather_main": weather_data.get("weather", {}).get("main")
                    }
                )
                
                alert_id = await AlertRepository.insert_alert(alert)
                logger.warning(f"LOW TEMPERATURE ALERT: {city} - {temp_current}°C")
                
                await AlertService._send_notification(alert)
                
                return alert_id
                
        except Exception as e:
            logger.error(f"Error checking low temperature: {e}")
        
        return None
    
    @staticmethod
    async def _check_high_humidity(city: str, weather_data: Dict[str, Any]) -> Optional[str]:
        """Check for high humidity alert"""
        try:
            humidity = safe_float(weather_data.get("humidity", 0))
            threshold = settings.ALERT_HUMIDITY_HIGH
            
            if humidity > threshold:
                # Check cooldown period
                recent_alert = await AlertRepository.check_recent_similar_alert(
                    city,
                    AlertType.HIGH_HUMIDITY,
                    minutes=settings.ALERT_COOLDOWN_MINUTES
                )
                
                if recent_alert:
                    return None
                
                # Create alert
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.HIGH_HUMIDITY,
                    severity=AlertSeverity.INFO if humidity < threshold + 10 else AlertSeverity.WARNING,
                    message=f"High humidity alert: {humidity}% (threshold: {threshold}%)",
                    condition=AlertCondition(
                        threshold_type="humidity",
                        threshold_value=threshold,
                        actual_value=humidity,
                        operator=">",
                        unit="%"
                    ),
                    metadata={
                        "humidity": humidity,
                        "temperature": weather_data.get("temperature", {}).get("current"),
                        "weather_main": weather_data.get("weather", {}).get("main")
                    }
                )
                
                alert_id = await AlertRepository.insert_alert(alert)
                logger.warning(f"HIGH HUMIDITY ALERT: {city} - {humidity}%")
                
                await AlertService._send_notification(alert)
                
                return alert_id
                
        except Exception as e:
            logger.error(f"Error checking high humidity: {e}")
        
        return None
    
    @staticmethod
    async def _check_extreme_weather(city: str, weather_data: Dict[str, Any]) -> Optional[str]:
        """Check for extreme weather conditions"""
        try:
            weather_main = weather_data.get("weather", {}).get("main", "")
            
            if weather_main in settings.ALERT_EXTREME_WEATHER:
                # Check cooldown period
                recent_alert = await AlertRepository.check_recent_similar_alert(
                    city,
                    AlertType.EXTREME_WEATHER,
                    minutes=settings.ALERT_COOLDOWN_MINUTES
                )
                
                if recent_alert:
                    return None
                
                # Create alert
                alert = AlertLog(
                    city=city,
                    alert_type=AlertType.EXTREME_WEATHER,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Extreme weather alert: {weather_main}",
                    condition=AlertCondition(
                        threshold_type="weather_condition",
                        threshold_value=0,  # Not applicable
                        actual_value=0,
                        operator="in",
                        unit=None
                    ),
                    metadata={
                        "weather_main": weather_main,
                        "weather_description": weather_data.get("weather", {}).get("description"),
                        "temperature": weather_data.get("temperature", {}).get("current"),
                        "wind_speed": weather_data.get("wind", {}).get("speed")
                    }
                )
                
                alert_id = await AlertRepository.insert_alert(alert)
                logger.critical(f"EXTREME WEATHER ALERT: {city} - {weather_main}")
                
                await AlertService._send_notification(alert)
                
                return alert_id
                
        except Exception as e:
            logger.error(f"Error checking extreme weather: {e}")
        
        return None
    
    @staticmethod
    async def _send_notification(alert: AlertLog) -> None:
        """
        Send alert notification
        Currently logs to console; can be extended to email, SMS, webhook, etc.
        
        Args:
            alert: Alert to notify about
        """
        try:
            notification_message = (
                f"\n{'='*60}\n"
                f"🚨 WEATHER ALERT 🚨\n"
                f"{'='*60}\n"
                f"City: {alert.city}\n"
                f"Type: {alert.alert_type.value}\n"
                f"Severity: {alert.severity.value.upper()}\n"
                f"Message: {alert.message}\n"
                f"Time: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"{'='*60}\n"
            )
            
            logger.warning(notification_message)
            
            # TODO: Implement additional notification channels
            # - Email via SMTP
            # - SMS via Twilio
            # - Slack/Discord webhook
            # - Push notifications
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    @staticmethod
    async def get_active_alerts(city: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get active alerts
        
        Args:
            city: Filter by city (optional)
            limit: Maximum number of alerts
            
        Returns:
            List of alert documents
        """
        try:
            return await AlertRepository.get_active_alerts(city, limit)
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    @staticmethod
    async def get_recent_alerts(city: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get recent alerts for a city
        
        Args:
            city: City name
            hours: Number of hours to look back
            
        Returns:
            List of alert documents
        """
        try:
            return await AlertRepository.get_recent_alerts(city, hours)
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []
    
    @staticmethod
    async def acknowledge_alert(alert_id: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if successful
        """
        try:
            return await AlertRepository.acknowledge_alert(alert_id)
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    @staticmethod
    async def get_alert_stats(city: Optional[str] = None) -> Dict[str, Any]:
        """
        Get alert statistics
        
        Args:
            city: Filter by city (optional)
            
        Returns:
            Statistics dictionary
        """
        try:
            return await AlertRepository.get_alert_stats(city)
        except Exception as e:
            logger.error(f"Error getting alert stats: {e}")
            return {}
