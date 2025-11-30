"""
Test script to verify system functionality
"""

import asyncio
import httpx
from app.config.settings import settings
from app.services.weather_service import WeatherService
from app.services.dashboard_service import DashboardService
from app.services.alert_service import AlertService
from app.config.database import DatabaseManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def test_openweather_api():
    """Test OpenWeatherMap API connection"""
    logger.info("Testing OpenWeatherMap API...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                settings.OPENWEATHER_API_URL,
                params={
                    "q": f"{settings.DEFAULT_CITY},{settings.DEFAULT_COUNTRY_CODE}",
                    "appid": settings.OPENWEATHER_API_KEY,
                    "units": "metric",
                }
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✓ API connection successful")
            logger.info(f"  City: {data['name']}")
            logger.info(f"  Temperature: {data['main']['temp']}°C")
            logger.info(f"  Weather: {data['weather'][0]['main']}")
            return True
            
        except Exception as e:
            logger.error(f"✗ API connection failed: {e}")
            return False


async def test_database_connection():
    """Test MongoDB connection"""
    logger.info("Testing MongoDB connection...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # Test write operation
        weather_col = db_manager.get_collection("weather_raw")
        test_doc = {
            "city": "Test",
            "temperature": 25.0,
            "test": True
        }
        result = await weather_col.insert_one(test_doc)
        
        # Clean up test document
        await weather_col.delete_one({"_id": result.inserted_id})
        
        logger.info("✓ Database connection successful")
        await db_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


async def test_weather_fetch():
    """Test weather fetching and storage"""
    logger.info("Testing weather data fetch...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        service = WeatherService()
        result = await service.fetch_and_store_weather(
            settings.DEFAULT_CITY,
            settings.DEFAULT_COUNTRY_CODE
        )
        
        if result:
            logger.info("✓ Weather fetch successful")
            logger.info(f"  Temperature: {result.temperature}°C")
            logger.info(f"  Humidity: {result.humidity}%")
            logger.info(f"  Condition: {result.weather_condition}")
        else:
            logger.error("✗ Weather fetch returned None")
            
        await db_manager.close()
        return result is not None
        
    except Exception as e:
        logger.error(f"✗ Weather fetch failed: {e}")
        return False


async def test_dashboard_generation():
    """Test dashboard data generation"""
    logger.info("Testing dashboard generation...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        service = DashboardService()
        result = await service.generate_dashboard_summary(
            settings.DEFAULT_CITY,
            settings.DEFAULT_COUNTRY_CODE
        )
        
        if result:
            logger.info("✓ Dashboard generation successful")
            logger.info(f"  Hourly records: {len(result.hourly_trend)}")
            logger.info(f"  Daily records: {len(result.daily_trend)}")
            logger.info(f"  Total records: {result.data_quality.total_records}")
        else:
            logger.error("✗ Dashboard generation returned None")
            
        await db_manager.close()
        return result is not None
        
    except Exception as e:
        logger.error(f"✗ Dashboard generation failed: {e}")
        return False


async def test_alert_checking():
    """Test alert checking"""
    logger.info("Testing alert checking...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        service = AlertService()
        alerts = await service.check_and_create_alerts(
            settings.DEFAULT_CITY,
            settings.DEFAULT_COUNTRY_CODE
        )
        
        logger.info(f"✓ Alert checking successful")
        logger.info(f"  Alerts created: {len(alerts)}")
        
        for alert in alerts:
            logger.info(f"  - {alert.alert_type}: {alert.message}")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Alert checking failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Weather Monitoring System - System Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("OpenWeatherMap API", test_openweather_api),
        ("MongoDB Connection", test_database_connection),
        ("Weather Fetch", test_weather_fetch),
        ("Dashboard Generation", test_dashboard_generation),
        ("Alert Checking", test_alert_checking),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        success = await test_func()
        results.append((name, success))
        print()
    
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Please check the logs above.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
