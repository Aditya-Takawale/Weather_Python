# DEPRECATED - Legacy Static Method Architecture

This folder contains the old static-method service pattern and is **NO LONGER USED**.

## Current Architecture

The application now uses **OOP Layered Architecture** with feature-based modules.

Each service now:
1. Extends `BaseService` from `common/base_service.py`
2. Lives inside its feature module (e.g., `api/weather/weather_service.py`)
3. Is instantiated as a class (not static methods)
4. Has repository dependencies injected via constructor

## Migration Examples

**Old (DEPRECATED):**
```python
from app.services.weather_service import WeatherService
result = WeatherService.fetch_weather_data(city)  # Static method
```

**New (CURRENT):**
```python
from app.api.weather.weather_service import WeatherService
service = WeatherService()  # Class instantiation
result = await service.fetch_and_store_weather(city)  # Instance method
```

See `ARCHITECTURE_REFACTORING.md` for the complete migration guide.
