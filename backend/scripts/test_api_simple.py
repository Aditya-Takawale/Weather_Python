"""
Quick API Test - No Dependencies Required
Tests OpenWeatherMap API connection
"""

import urllib.request
import json

# Your configuration
# Get API key from environment or settings
from app.config.settings import settings
API_KEY = settings.OPENWEATHER_API_KEY
CITY = "Pune"
COUNTRY = "IN"
API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY}&appid={API_KEY}&units=metric"

print("="*60)
print("🌤️  Testing OpenWeatherMap API")
print("="*60)
print(f"\n📍 City: {CITY}, {COUNTRY}")
print(f"🔑 API Key: {API_KEY[:10]}...")
print(f"\n🔗 Request URL:")
print(f"   {API_URL}")
print("\n⏳ Fetching weather data...\n")

try:
    with urllib.request.urlopen(API_URL, timeout=10) as response:
        data = json.loads(response.read().decode())
        
        print("✅ SUCCESS! API is working!")
        print("="*60)
        print("\n📊 Current Weather Data:")
        print("-"*60)
        print(f"🏙️  Location:     {data['name']}, {data['sys']['country']}")
        print(f"🌡️  Temperature:  {data['main']['temp']}°C")
        print(f"🌡️  Feels Like:   {data['main']['feels_like']}°C")
        print(f"📊 Min/Max:      {data['main']['temp_min']}°C / {data['main']['temp_max']}°C")
        print(f"☁️  Weather:      {data['weather'][0]['main']} - {data['weather'][0]['description']}")
        print(f"💧 Humidity:     {data['main']['humidity']}%")
        print(f"🌀 Pressure:     {data['main']['pressure']} hPa")
        print(f"💨 Wind Speed:   {data['wind']['speed']} m/s")
        print(f"🧭 Wind Dir:     {data['wind'].get('deg', 'N/A')}°")
        print(f"👁️  Visibility:   {data.get('visibility', 'N/A')} meters")
        print(f"☁️  Cloudiness:   {data['clouds']['all']}%")
        
        print("\n" + "="*60)
        print("✨ Your API key is working perfectly!")
        print("="*60)
        
        print("\n📝 Raw JSON Response:")
        print(json.dumps(data, indent=2))
        
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    print(f"\n💡 This usually means:")
    if e.code == 401:
        print("   - Invalid API key")
        print("   - Check your API key at: https://openweathermap.org/api")
    elif e.code == 404:
        print("   - City not found")
        print("   - Check the city name spelling")
    else:
        print(f"   - Server error: {e.code}")
    
except urllib.error.URLError as e:
    print(f"❌ Connection Error: {e.reason}")
    print("\n💡 This usually means:")
    print("   - No internet connection")
    print("   - Firewall blocking the request")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")

print("\n" + "="*60)
print("🔗 Next Steps:")
print("="*60)
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Test full system: python test_connection.py")
print("3. Start the server: uvicorn app.main:app --reload")
print("="*60)
