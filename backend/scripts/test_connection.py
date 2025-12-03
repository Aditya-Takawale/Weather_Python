"""
Test MongoDB Connection and OpenWeatherMap API
Quick script to verify system connectivity
"""

import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from app.infrastructure.config import settings

async def test_mongodb():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB Connection...")
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        
        # List databases
        db_list = await client.list_database_names()
        print(f"✅ MongoDB Connected!")
        print(f"   URL: {settings.MONGODB_URL}")
        print(f"   Available databases: {db_list}")
        
        # Check if weather_dashboard exists
        if settings.MONGODB_DB_NAME in db_list:
            db = client[settings.MONGODB_DB_NAME]
            collections = await db.list_collection_names()
            print(f"\n📊 Collections in '{settings.MONGODB_DB_NAME}':")
            for coll in collections:
                count = await db[coll].count_documents({})
                print(f"   - {coll}: {count} documents")
        else:
            print(f"\n⚠️  Database '{settings.MONGODB_DB_NAME}' not found. Will be created on first use.")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        return False

async def test_openweather_api():
    """Test OpenWeatherMap API"""
    print("\n🌤️  Testing OpenWeatherMap API...")
    try:
        url = f"{settings.OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": f"{settings.OPENWEATHER_CITY},{settings.OPENWEATHER_COUNTRY_CODE}",
            "appid": settings.OPENWEATHER_API_KEY,
            "units": settings.OPENWEATHER_UNITS
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ OpenWeatherMap API Connected!")
            print(f"   City: {data.get('name')}, {data.get('sys', {}).get('country')}")
            print(f"   Temperature: {data.get('main', {}).get('temp')}°C")
            print(f"   Weather: {data.get('weather', [{}])[0].get('description')}")
            print(f"   Humidity: {data.get('main', {}).get('humidity')}%")
            print(f"   Wind Speed: {data.get('wind', {}).get('speed')} m/s")
            
        return True
    except httpx.HTTPStatusError as e:
        print(f"❌ API Request Failed: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ OpenWeatherMap API Error: {e}")
        return False

async def test_redis():
    """Test Redis connection (if redis-py is available)"""
    print("\n🔴 Testing Redis Connection...")
    try:
        import redis.asyncio as redis
        r = await redis.from_url(settings.REDIS_URL)
        await r.ping()
        print(f"✅ Redis Connected!")
        print(f"   URL: {settings.REDIS_URL}")
        await r.close()
        return True
    except ImportError:
        print("⚠️  redis package not installed (install with: pip install redis)")
        return None
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")
        return False

async def main():
    """Run all connection tests"""
    print("="*60)
    print("🧪 Weather Monitoring System - Connection Tests")
    print("="*60)
    
    # Test MongoDB
    mongo_ok = await test_mongodb()
    
    # Test OpenWeatherMap API
    api_ok = await test_openweather_api()
    
    # Test Redis
    redis_ok = await test_redis()
    
    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary")
    print("="*60)
    print(f"MongoDB:          {'✅ PASS' if mongo_ok else '❌ FAIL'}")
    print(f"OpenWeatherMap:   {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Redis:            {'✅ PASS' if redis_ok else '⚠️  SKIP' if redis_ok is None else '❌ FAIL'}")
    
    if mongo_ok and api_ok:
        print("\n✨ All critical tests passed! System is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("   2. Start Celery worker: celery -A app.tasks.celery_app worker -l info")
        print("   3. Start Celery beat: celery -A app.tasks.celery_app beat -l info")
        print("   4. Access API docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
