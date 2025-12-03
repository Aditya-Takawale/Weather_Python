"""
Script to populate historical weather data for the past 7 days
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import logging
from datetime import datetime, timedelta
from app.infrastructure.database import DatabaseManager
from app.api.weather.weather_repository import WeatherRepository
from app.models.weather import WeatherRaw, WeatherTemperature, WeatherCondition, WeatherWind

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def populate_historical_data():
    """Populate historical weather data for the past 7 days"""
    try:
        # Initialize database
        await DatabaseManager.connect()
        logger.info("Connected to database")
        
        cities = ["Pune"]
        days = 7
        
        logger.info(f"Generating {days} days of historical data for {len(cities)} cities...")
        
        for city in cities:
            logger.info(f"\nProcessing {city}...")
            
            # Generate data for each day
            for day in range(days):
                # Calculate date
                target_date = datetime.utcnow() - timedelta(days=day)
                
                # Generate multiple records throughout the day (every 3 hours = 8 records per day)
                for hour in range(0, 24, 3):
                    timestamp = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # Generate realistic temperature variations
                    base_temp = 22  # Base temperature
                    temp_variation = 5 * (1 - abs(hour - 14) / 14)  # Peak at 2 PM
                    day_variation = day * 0.5  # Slight variation across days
                    temperature = base_temp + temp_variation - day_variation
                    
                    # Temperature ranges
                    temp_min = temperature - 2
                    temp_max = temperature + 2
                    feels_like = temperature + 1
                    
                    # Humidity (higher in morning/evening)
                    humidity = 40 + (20 if hour < 6 or hour > 18 else 0)
                    
                    # Weather conditions
                    weather_conditions = ["Clear", "Clouds", "Haze"]
                    weather_main = weather_conditions[day % len(weather_conditions)]
                    
                    # Create WeatherRaw model
                    weather_data = WeatherRaw(
                        city=city,
                        timestamp=timestamp,
                        temperature=WeatherTemperature(
                            current=round(temperature, 1),
                            feels_like=round(feels_like, 1),
                            min=round(temp_min, 1),
                            max=round(temp_max, 1)
                        ),
                        humidity=int(humidity),
                        pressure=1013,
                        weather=WeatherCondition(
                            main=weather_main,
                            description=weather_main.lower(),
                            icon="01d" if weather_main == "Clear" else "02d"
                        ),
                        wind=WeatherWind(
                            speed=round(1.5 + (day * 0.2), 2),
                            deg=90
                        ),
                        clouds=20 if weather_main == "Clear" else 50,
                        visibility=10000,
                        sunrise=timestamp.replace(hour=6, minute=50),
                        sunset=timestamp.replace(hour=17, minute=56),
                        data_source="historical_simulation"
                    )
                    
                    # Insert into database
                    repository = WeatherRepository()
                    await repository.insert_weather_data(weather_data)
                
                logger.info(f"✓ Generated data for {target_date.strftime('%Y-%m-%d')}")
        
        logger.info("\n✓ Historical data population completed!")
        logger.info("Now run: python populate_data.py to generate dashboard summary")
        
    except Exception as e:
        logger.error(f"Error populating historical data: {e}")
        raise
    finally:
        await DatabaseManager.disconnect()


if __name__ == "__main__":
    asyncio.run(populate_historical_data())
