"""
Dashboard Service
Business logic for aggregating and computing dashboard summary data
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

from ..models.dashboard import (
    DashboardSummary,
    CurrentWeather,
    TodayStats,
    HourlyTrend,
    DailyTrend
)
from ..repositories.weather_repository import WeatherRepository
from ..repositories.dashboard_repository import DashboardRepository
from ..utils.logger import get_logger
from ..utils.helpers import safe_float, safe_int

logger = get_logger(__name__)


class DashboardService:
    """Service for dashboard data aggregation and management"""
    
    @staticmethod
    async def generate_dashboard_summary(city: str) -> Optional[DashboardSummary]:
        """
        Generate comprehensive dashboard summary from raw weather data
        Performs all necessary aggregations and computations
        
        Args:
            city: City name
            
        Returns:
            DashboardSummary instance or None
        """
        try:
            logger.info(f"Generating dashboard summary for {city}")
            
            # Get latest weather data
            latest_weather = await WeatherRepository.get_latest_weather(city)
            if not latest_weather:
                logger.warning(f"No weather data found for {city}")
                return None
            
            # Generate current weather snapshot
            current_weather = DashboardService._build_current_weather(latest_weather)
            
            # Generate today's statistics
            today_stats = await DashboardService._generate_today_stats(city)
            
            # Generate hourly trend (last 24 hours)
            hourly_trend = await DashboardService._generate_hourly_trend(city, hours=24)
            
            # Generate daily trend (last 7 days)
            daily_trend = await DashboardService._generate_daily_trend(city, days=7)
            
            # Generate weather distribution
            weather_distribution = await WeatherRepository.get_weather_distribution(city, hours=24)
            
            # Build dashboard summary
            dashboard_summary = DashboardSummary(
                city=city,
                summary_type="hourly",
                generated_at=datetime.utcnow(),
                current_weather=current_weather,
                today_stats=today_stats,
                hourly_trend=hourly_trend,
                daily_trend=daily_trend,
                weather_distribution=weather_distribution
            )
            
            logger.info(f"Successfully generated dashboard summary for {city}")
            return dashboard_summary
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return None
    
    @staticmethod
    def _build_current_weather(weather_doc: Dict[str, Any]) -> CurrentWeather:
        """
        Build CurrentWeather model from weather document
        
        Args:
            weather_doc: Weather document from database
            
        Returns:
            CurrentWeather instance
        """
        temp_data = weather_doc.get("temperature", {})
        weather_data = weather_doc.get("weather", {})
        wind_data = weather_doc.get("wind", {})
        
        return CurrentWeather(
            temperature=safe_float(temp_data.get("current", 0)),
            feels_like=safe_float(temp_data.get("feels_like", 0)),
            humidity=safe_float(weather_doc.get("humidity", 0)),
            pressure=safe_int(weather_doc.get("pressure", 0)),
            weather_main=weather_data.get("main", "Unknown"),
            weather_description=weather_data.get("description", ""),
            weather_icon=weather_data.get("icon", ""),
            wind_speed=safe_float(wind_data.get("speed", 0)),
            wind_deg=safe_int(wind_data.get("deg", 0)),
            clouds=safe_int(weather_doc.get("clouds", 0)),
            visibility=safe_int(weather_doc.get("visibility", 0)),
            sunrise=weather_doc.get("sunrise"),
            sunset=weather_doc.get("sunset")
        )
    
    @staticmethod
    async def _generate_today_stats(city: str) -> TodayStats:
        """
        Generate aggregated statistics for today
        
        Args:
            city: City name
            
        Returns:
            TodayStats instance
        """
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            stats = await WeatherRepository.get_weather_stats(city, today_start, today_end)
            
            if not stats:
                # Return defaults if no data
                return TodayStats(
                    temp_avg=0,
                    temp_min=0,
                    temp_max=0,
                    humidity_avg=0,
                    humidity_min=0,
                    humidity_max=0,
                    pressure_avg=0,
                    wind_speed_avg=0,
                    records_count=0
                )
            
            return TodayStats(
                temp_avg=round(safe_float(stats.get("temp_avg", 0)), 1),
                temp_min=round(safe_float(stats.get("temp_min", 0)), 1),
                temp_max=round(safe_float(stats.get("temp_max", 0)), 1),
                humidity_avg=round(safe_float(stats.get("humidity_avg", 0)), 1),
                humidity_min=round(safe_float(stats.get("humidity_min", 0)), 1),
                humidity_max=round(safe_float(stats.get("humidity_max", 0)), 1),
                pressure_avg=safe_int(stats.get("pressure_avg", 0)),
                wind_speed_avg=round(safe_float(stats.get("wind_speed_avg", 0)), 1),
                records_count=safe_int(stats.get("count", 0))
            )
            
        except Exception as e:
            logger.error(f"Error generating today stats: {e}")
            return TodayStats(
                temp_avg=0, temp_min=0, temp_max=0,
                humidity_avg=0, humidity_min=0, humidity_max=0,
                pressure_avg=0, wind_speed_avg=0, records_count=0
            )
    
    @staticmethod
    async def _generate_hourly_trend(city: str, hours: int = 24) -> List[HourlyTrend]:
        """
        Generate hourly trend data for the last N hours
        
        Args:
            city: City name
            hours: Number of hours to include
            
        Returns:
            List of HourlyTrend instances
        """
        try:
            weather_data = await WeatherRepository.get_weather_last_n_hours(city, hours)
            
            if not weather_data:
                return []
            
            # Group by hour
            hourly_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            
            for record in weather_data:
                # Round timestamp to nearest hour
                timestamp = record.get("timestamp")
                if not timestamp:
                    continue
                
                hour_key = timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
                hourly_groups[hour_key].append(record)
            
            # Aggregate each hour
            hourly_trends = []
            for hour_key in sorted(hourly_groups.keys(), reverse=True)[:24]:
                records = hourly_groups[hour_key]
                
                # Calculate averages
                temps = [safe_float(r.get("temperature", {}).get("current", 0)) for r in records]
                humidities = [safe_float(r.get("humidity", 0)) for r in records]
                wind_speeds = [safe_float(r.get("wind", {}).get("speed", 0)) for r in records]
                
                # Get most common weather condition
                weather_conditions = [r.get("weather", {}).get("main", "Unknown") for r in records]
                most_common_weather = max(set(weather_conditions), key=weather_conditions.count)
                
                hourly_trend = HourlyTrend(
                    hour=datetime.fromisoformat(hour_key),
                    temperature=round(sum(temps) / len(temps), 1) if temps else 0,
                    humidity=round(sum(humidities) / len(humidities), 1) if humidities else 0,
                    weather_main=most_common_weather,
                    wind_speed=round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else 0
                )
                
                hourly_trends.append(hourly_trend)
            
            # Sort by hour (oldest first for chart display)
            hourly_trends.sort(key=lambda x: x.hour)
            
            return hourly_trends
            
        except Exception as e:
            logger.error(f"Error generating hourly trend: {e}")
            return []
    
    @staticmethod
    async def _generate_daily_trend(city: str, days: int = 7) -> List[DailyTrend]:
        """
        Generate daily trend data for the last N days
        
        Args:
            city: City name
            days: Number of days to include
            
        Returns:
            List of DailyTrend instances
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            weather_data = await WeatherRepository.get_weather_by_time_range(city, start_time, end_time)
            
            if not weather_data:
                return []
            
            # Group by date
            daily_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            
            for record in weather_data:
                timestamp = record.get("timestamp")
                if not timestamp:
                    continue
                
                date_key = timestamp.strftime("%Y-%m-%d")
                daily_groups[date_key].append(record)
            
            # Aggregate each day
            daily_trends = []
            for date_key in sorted(daily_groups.keys(), reverse=True)[:days]:
                records = daily_groups[date_key]
                
                # Calculate statistics
                temps = [safe_float(r.get("temperature", {}).get("current", 0)) for r in records]
                temp_mins = [safe_float(r.get("temperature", {}).get("min", 0)) for r in records]
                temp_maxs = [safe_float(r.get("temperature", {}).get("max", 0)) for r in records]
                humidities = [safe_float(r.get("humidity", 0)) for r in records]
                
                # Get most common weather condition
                weather_conditions = [r.get("weather", {}).get("main", "Unknown") for r in records]
                most_common_weather = max(set(weather_conditions), key=weather_conditions.count)
                
                daily_trend = DailyTrend(
                    date=date_key,
                    temp_avg=round(sum(temps) / len(temps), 1) if temps else 0,
                    temp_min=round(min(temp_mins), 1) if temp_mins else 0,
                    temp_max=round(max(temp_maxs), 1) if temp_maxs else 0,
                    humidity_avg=round(sum(humidities) / len(humidities), 1) if humidities else 0,
                    weather_main=most_common_weather,
                    records_count=len(records)
                )
                
                daily_trends.append(daily_trend)
            
            # Sort by date (oldest first for chart display)
            daily_trends.sort(key=lambda x: x.date)
            
            return daily_trends
            
        except Exception as e:
            logger.error(f"Error generating daily trend: {e}")
            return []
    
    @staticmethod
    async def save_dashboard_summary(summary: DashboardSummary) -> bool:
        """
        Save dashboard summary to database
        
        Args:
            summary: DashboardSummary instance
            
        Returns:
            True if successful
        """
        try:
            await DashboardRepository.upsert_summary(summary)
            logger.info(f"Saved dashboard summary for {summary.city}")
            return True
        except Exception as e:
            logger.error(f"Error saving dashboard summary: {e}")
            return False
    
    @staticmethod
    async def get_latest_dashboard_summary(city: str) -> Optional[Dict[str, Any]]:
        """
        Get latest dashboard summary from database
        
        Args:
            city: City name
            
        Returns:
            Dashboard summary document or None
        """
        try:
            return await DashboardRepository.get_latest_summary(city)
        except Exception as e:
            logger.error(f"Error getting latest dashboard summary: {e}")
            return None
