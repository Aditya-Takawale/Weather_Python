"""
Script to populate weather data and generate dashboard summary
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import logging
from app.config.settings import settings
from app.config.database import DatabaseManager
from app.api.weather.weather_service import WeatherService
from app.api.dashboard.dashboard_service import DashboardService

logger = logging.getLogger(__name__)


async def populate_data():
    """Fetch weather data and generate dashboard summary"""
    try:
        # Initialize database
        await DatabaseManager.connect()
        logger.info(f"Connected to database: {settings.MONGODB_DB_NAME}")
        
        # Initialize services
        weather_service = WeatherService()
        dashboard_service = DashboardService()
        
        # Cities to fetch - Only Pune
        cities = ["Pune"]
        
        logger.info(f"Fetching weather data for {len(cities)} city...")
        
        # Fetch weather for each city
        for city in cities:
            try:
                logger.info(f"Fetching weather for {city}...")
                success = await weather_service.fetch_and_store_weather(city)
                if success:
                    logger.info(f"✓ Stored weather data for {city}")
                else:
                    logger.warning(f"✗ Failed to fetch weather for {city}")
            except Exception as e:
                logger.error(f"✗ Error fetching weather for {city}: {e}")
        
        logger.info("\nGenerating dashboard summaries...")
        
        # Generate dashboard summaries for each city
        for city in cities:
            try:
                logger.info(f"Generating dashboard summary for {city}...")
                summary = await dashboard_service.generate_dashboard_summary(city)
                if summary:
                    await dashboard_service.save_dashboard_summary(summary)
                    logger.info(f"✓ Generated dashboard summary for {city}")
                    logger.info(f"  - Avg Temp: {summary.today_stats.temp_avg:.1f}°C")
                    logger.info(f"  - Max Temp: {summary.today_stats.temp_max:.1f}°C")
                    logger.info(f"  - Min Temp: {summary.today_stats.temp_min:.1f}°C")
                else:
                    logger.warning(f"✗ No data available to generate summary for {city}")
            except Exception as e:
                logger.error(f"✗ Error generating summary for {city}: {e}")
        
        logger.info("\n✓ Data population completed!")
        logger.info("You can now refresh the dashboard at http://localhost:3000")
        
    except Exception as e:
        logger.error(f"Error populating data: {e}")
        raise
    finally:
        await DatabaseManager.disconnect()


if __name__ == "__main__":
    asyncio.run(populate_data())
