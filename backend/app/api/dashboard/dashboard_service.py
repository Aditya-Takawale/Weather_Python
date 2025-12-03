"""
Dashboard Service
Business logic for aggregating and computing dashboard summary data using OOP pattern
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

from ...common.base_service import BaseService
from ...common.exceptions import NotFoundException, InternalServerException
from ...common.decorators import log_execution, handle_exceptions
from ...models.dashboard import (
    DashboardSummary,
    CurrentWeather,
    TodayStats,
    HourlyTrend,
    DailyTrend
)
from ...core.utils import safe_float, safe_int
from ..weather.weather_repository import WeatherRepository
from .dashboard_repository import DashboardRepository


class DashboardService(BaseService[DashboardSummary]):
    """Service for dashboard data aggregation and management"""
    
    def __init__(self):
        """Initialize dashboard service with repositories"""
        super().__init__()
        self.repository = DashboardRepository()
        self.weather_repository = WeatherRepository()
    
    @log_execution
    @handle_exceptions
    async def generate_dashboard_summary(self, city: str) -> Optional[DashboardSummary]:
        """
        Generate comprehensive dashboard summary from raw weather data
        Performs all necessary aggregations and computations
        
        Args:
            city: City name
            
        Returns:
            DashboardSummary instance or None
        """
        try:
            self._log_info("Generating dashboard summary for %s", city)
            
            # Get latest weather data
            latest_weather = await self.weather_repository.get_latest_weather(city)
            if not latest_weather:
                self._log_warning("No weather data found for %s", city)
                return None
            
            # Generate current weather snapshot
            current_weather = self._build_current_weather(latest_weather)
            
            # Generate today's statistics
            today_stats = await self._generate_today_stats(city)
            
            # Generate hourly trend (last 24 hours)
            hourly_trend = await self._generate_hourly_trend(city, hours=24)
            
            # Generate daily trend (last 7 days)
            daily_trend = await self._generate_daily_trend(city, days=7)
            
            # Generate weather distribution
            weather_distribution = await self.weather_repository.get_weather_distribution(
                city,
                hours=24
            )
            
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
            
            self._log_info("Successfully generated dashboard summary for %s", city)
            return dashboard_summary
            
        except Exception as e:
            self._log_error("Error generating dashboard summary: %s", e)
            return None
    
    def _build_current_weather(self, weather_doc: Dict[str, Any]) -> CurrentWeather:
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
    
    async def _generate_today_stats(self, city: str) -> TodayStats:
        """
        Generate aggregated statistics for today
        
        Args:
            city: City name
            
        Returns:
            TodayStats instance
        """
        try:
            today_start = datetime.utcnow().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            today_end = today_start + timedelta(days=1)
            
            stats = await self.weather_repository.get_weather_stats(
                city,
                today_start,
                today_end
            )
            
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
            self._log_error("Error generating today stats: %s", e)
            return TodayStats(
                temp_avg=0, temp_min=0, temp_max=0,
                humidity_avg=0, humidity_min=0, humidity_max=0,
                pressure_avg=0, wind_speed_avg=0, records_count=0
            )
    
    async def _generate_hourly_trend(
        self,
        city: str,
        hours: int = 24
    ) -> List[HourlyTrend]:
        """
        Generate hourly trend data for the last N hours
        
        Args:
            city: City name
            hours: Number of hours to include
            
        Returns:
            List of HourlyTrend instances
        """
        try:
            weather_data = await self.weather_repository.get_weather_last_n_hours(
                city,
                hours
            )
            
            if not weather_data:
                return []
            
            # Group by hour
            hourly_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            
            for record in weather_data:
                # Round timestamp to nearest hour
                timestamp = record.get("timestamp")
                if not timestamp:
                    continue
                
                hour_key = timestamp.replace(
                    minute=0,
                    second=0,
                    microsecond=0
                ).isoformat()
                hourly_groups[hour_key].append(record)
            
            # Aggregate each hour
            hourly_trends = []
            for hour_key in sorted(hourly_groups.keys(), reverse=True)[:24]:
                records = hourly_groups[hour_key]
                
                # Calculate averages
                temps = [
                    safe_float(r.get("temperature", {}).get("current", 0))
                    for r in records
                ]
                humidities = [safe_float(r.get("humidity", 0)) for r in records]
                wind_speeds = [
                    safe_float(r.get("wind", {}).get("speed", 0))
                    for r in records
                ]
                
                # Get most common weather condition
                weather_conditions = [
                    r.get("weather", {}).get("main", "Unknown")
                    for r in records
                ]
                most_common_weather = max(
                    set(weather_conditions),
                    key=weather_conditions.count
                )
                
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
            self._log_error("Error generating hourly trend: %s", e)
            return []
    
    async def _generate_daily_trend(
        self,
        city: str,
        days: int = 7
    ) -> List[DailyTrend]:
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
            
            weather_data = await self.weather_repository.get_weather_by_time_range(
                city,
                start_time,
                end_time
            )
            
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
                temps = [
                    safe_float(r.get("temperature", {}).get("current", 0))
                    for r in records
                ]
                temp_mins = [
                    safe_float(r.get("temperature", {}).get("min", 0))
                    for r in records
                ]
                temp_maxs = [
                    safe_float(r.get("temperature", {}).get("max", 0))
                    for r in records
                ]
                humidities = [safe_float(r.get("humidity", 0)) for r in records]
                
                # Get most common weather condition
                weather_conditions = [
                    r.get("weather", {}).get("main", "Unknown")
                    for r in records
                ]
                most_common_weather = max(
                    set(weather_conditions),
                    key=weather_conditions.count
                )
                
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
            self._log_error("Error generating daily trend: %s", e)
            return []
    
    @log_execution
    @handle_exceptions
    async def save_dashboard_summary(self, summary: DashboardSummary) -> bool:
        """
        Save dashboard summary to database
        
        Args:
            summary: DashboardSummary instance
            
        Returns:
            True if successful
        """
        try:
            await self.repository.upsert_summary(summary)
            self._log_info("Saved dashboard summary for %s", summary.city)
            return True
            
        except Exception as e:
            self._log_error("Error saving dashboard summary: %s", e)
            return False
    
    @log_execution
    @handle_exceptions
    async def get_latest_dashboard_summary(
        self,
        city: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest dashboard summary from database
        
        Args:
            city: City name
            
        Returns:
            Dashboard summary document or None
            
        Raises:
            NotFoundException: If no summary found
        """
        try:
            summary = await self.repository.get_latest_summary(city)
            
            if not summary:
                raise NotFoundException(
                    message=f"No dashboard summary found for city: {city}",
                    details={"city": city}
                )
            
            return summary
            
        except NotFoundException:
            raise
        except Exception as e:
            self._log_error("Error getting latest dashboard summary: %s", e)
            raise InternalServerException(
                message="Failed to retrieve dashboard summary",
                details={"city": city, "error": str(e)}
            )
