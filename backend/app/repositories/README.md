# DEPRECATED - Legacy Static Method Architecture

This folder contains the old static-method repository pattern and is **NO LONGER USED**.

## Current Architecture

The application now uses **OOP Layered Architecture** with feature-based modules.

Each repository now:
1. Extends `BaseRepository[T]` from `common/base_repository.py`
2. Lives inside its feature module (e.g., `api/weather/weather_repository.py`)
3. Is instantiated as a class (not static methods)

## Migration Examples

**Old (DEPRECATED):**
```python
from app.repositories.weather_repository import WeatherRepository
result = WeatherRepository.insert_weather_data(data)  # Static method
```

**New (CURRENT):**
```python
from app.api.weather.weather_repository import WeatherRepository
repository = WeatherRepository()  # Class instantiation
result = await repository.insert_weather_data(data)  # Instance method
```

See `ARCHITECTURE_REFACTORING.md` for the complete migration guide.
