# Backend Architecture Pattern

## Architecture Type: **Layered Architecture with Feature Modules**

This backend follows the **"Clean Architecture"** pattern, also known as:
- **Layered Architecture** (most common name)
- **Hexagonal Architecture** (Ports and Adapters)
- **Onion Architecture**
- **Feature-based Modular Architecture** (when organized by features)

Similar implementations can be found in:
- **NestJS** (Node.js/TypeScript framework)
- **Spring Boot** (Java)
- **Django REST Framework** (Python, when using apps)
- **.NET Core** (C#)

## Current Structure

```
backend/app/
├── api/                          # Feature Modules
│   ├── weather/                  # Weather feature
│   │   ├── weather_repository.py    # Data Access Layer
│   │   ├── weather_service.py       # Business Logic Layer
│   │   ├── weather_controller.py    # Presentation Layer
│   │   ├── weather_router.py        # API Routes Layer
│   │   └── __init__.py
│   ├── dashboard/                # Dashboard feature
│   │   ├── dashboard_repository.py
│   │   ├── dashboard_service.py
│   │   ├── dashboard_controller.py
│   │   ├── dashboard_router.py
│   │   └── __init__.py
│   ├── alerts/                   # Alerts feature
│   │   ├── alert_repository.py
│   │   ├── alert_service.py
│   │   ├── alert_controller.py
│   │   ├── alert_router.py
│   │   └── __init__.py
│   └── routes/                   # Legacy (backward compatibility)
│       ├── __init__.py (imports from new structure)
│       ├── weather.py (deprecated)
│       ├── dashboard.py (deprecated)
│       └── alerts.py (deprecated)
│
├── common/                       # Shared Infrastructure
│   ├── base_repository.py       # Generic repository base
│   ├── base_service.py          # Generic service base
│   ├── base_controller.py       # Generic controller base
│   ├── exceptions.py            # Custom HTTP exceptions
│   ├── decorators.py            # Cross-cutting concerns
│   └── __init__.py
│
├── tasks/                        # Background Jobs (Celery)
│   ├── celery_app.py
│   ├── weather_tasks.py         # Uses new OOP services
│   ├── dashboard_tasks.py       # Uses new OOP services
│   ├── alert_tasks.py           # Uses new OOP services
│   └── cleanup_tasks.py         # Uses new OOP repositories
│
├── models/                       # Domain Models (Pydantic)
│   ├── weather.py
│   ├── dashboard.py
│   └── alert.py
│
├── config/                       # Configuration
│   ├── settings.py
│   └── database.py
│
├── utils/                        # Utilities
│   ├── logger.py
│   └── helpers.py
│
├── services/                     # ⚠️ LEGACY - Not used
│   ├── weather_service.py       # Replaced by api/weather/
│   ├── dashboard_service.py     # Replaced by api/dashboard/
│   └── alert_service.py         # Replaced by api/alerts/
│
├── repositories/                 # ⚠️ LEGACY - Not used
│   ├── weather_repository.py    # Replaced by api/weather/
│   ├── dashboard_repository.py  # Replaced by api/dashboard/
│   └── alert_repository.py      # Replaced by api/alerts/
│
└── main.py                       # FastAPI Application Entry Point
```

## Layer Responsibilities

### 1. **Router Layer** (weather_router.py)
- **Purpose**: Define HTTP routes and endpoints
- **Dependencies**: Controller
- **Responsibility**: URL routing, FastAPI route definitions
- **Example**:
```python
@router.get("/current")
async def get_current_weather(city: str):
    return await weather_controller.get_current_weather(city)
```

### 2. **Controller Layer** (weather_controller.py)
- **Purpose**: Handle HTTP requests/responses
- **Dependencies**: Service
- **Responsibility**: Request validation, response formatting, error handling
- **Example**:
```python
class WeatherController(BaseController):
    def __init__(self):
        self.service = WeatherService()
    
    async def get_current_weather(self, city: str):
        weather_data = await self.service.get_latest_weather(city)
        return self.success_response(data=weather_data)
```

### 3. **Service Layer** (weather_service.py)
- **Purpose**: Business logic and orchestration
- **Dependencies**: Repository, external APIs
- **Responsibility**: Business rules, data transformation, orchestration
- **Example**:
```python
class WeatherService(BaseService):
    def __init__(self):
        self.repository = WeatherRepository()
    
    async def get_latest_weather(self, city: str):
        # Business logic
        data = await self.repository.get_latest_weather(city)
        if not data:
            raise NotFoundException(f"No data for {city}")
        return data
```

### 4. **Repository Layer** (weather_repository.py)
- **Purpose**: Data access and persistence
- **Dependencies**: Database
- **Responsibility**: CRUD operations, database queries
- **Example**:
```python
class WeatherRepository(BaseRepository):
    def __init__(self):
        super().__init__("weather_collection")
    
    async def get_latest_weather(self, city: str):
        return await self.find_one(
            {"city": city},
            sort=[("timestamp", -1)]
        )
```

## Design Principles

### 1. **Separation of Concerns (SoC)**
Each layer has a single, well-defined responsibility:
- Router: Routes
- Controller: HTTP
- Service: Business Logic
- Repository: Data Access

### 2. **Dependency Inversion Principle (DIP)**
High-level modules (Service) don't depend on low-level modules (Repository). Both depend on abstractions (BaseRepository, BaseService).

### 3. **Single Responsibility Principle (SRP)**
Each class has one reason to change:
- Repository changes only when data storage changes
- Service changes only when business rules change
- Controller changes only when HTTP handling changes

### 4. **Open/Closed Principle (OCP)**
Classes are open for extension (inheritance from base classes) but closed for modification (base classes are stable).

### 5. **Don't Repeat Yourself (DRY)**
Common functionality extracted to base classes:
- BaseRepository: 10 CRUD methods
- BaseService: Logging helpers
- BaseController: Response formatting
- Decorators: Cross-cutting concerns

### 6. **Dependency Injection (DI)**
Dependencies are injected through constructors:
```python
class WeatherService:
    def __init__(self):
        self.repository = WeatherRepository()  # DI
```

## Request Flow

```
HTTP Request
    ↓
FastAPI Router (weather_router.py)
    ↓
Controller (weather_controller.py)
    ├─→ Validates request
    ├─→ Calls service
    └─→ Formats response
        ↓
Service (weather_service.py)
    ├─→ Applies business logic
    ├─→ Calls repository
    └─→ Transforms data
        ↓
Repository (weather_repository.py)
    ├─→ Queries database
    └─→ Returns data
        ↓
MongoDB
```

## Benefits

### ✅ Maintainability
- Clear structure makes code easy to find and modify
- Changes in one layer don't affect others
- New developers can understand the codebase quickly

### ✅ Testability
- Each layer can be tested independently
- Easy to mock dependencies (inject mock repository into service)
- Unit tests, integration tests, and E2E tests are straightforward

### ✅ Scalability
- Easy to add new features (create new folder in api/)
- Can replace implementations without changing other layers
- Horizontal scaling is simplified

### ✅ Reusability
- Base classes eliminate duplicate code
- Services can be reused in different contexts (API, CLI, Celery)
- Repositories can be swapped (MongoDB → PostgreSQL)

### ✅ Security
- Clear boundaries prevent unauthorized access
- Input validation at controller layer
- Business rules enforcement at service layer

## Comparison with Other Patterns

### vs. MVC (Model-View-Controller)
- **MVC**: Model ↔ View ↔ Controller
- **Layered**: Router → Controller → Service → Repository
- **Advantage**: More layers = better separation of concerns

### vs. Three-tier Architecture
- **Three-tier**: Presentation → Business → Data
- **Layered**: Same concept, but more granular (4-5 layers)
- **Advantage**: Controller and Router are separated

### vs. Microservices
- **Microservices**: Multiple independent services
- **Layered**: Single monolithic application with modular structure
- **Advantage**: Simpler to develop, deploy, and debug initially

## Migration Status

### ✅ Completed
- [x] Base classes created (common/)
- [x] Weather module refactored (api/weather/)
- [x] Dashboard module refactored (api/dashboard/)
- [x] Alerts module refactored (api/alerts/)
- [x] Celery tasks updated
- [x] Scripts updated
- [x] Routes integration updated

### ⚠️ Legacy (Keep for reference)
- [ ] services/ folder (old static methods)
- [ ] repositories/ folder (old static methods)
- [ ] api/routes/*.py (old route files)

These legacy files are kept for backward compatibility and reference. They have deprecation notices and import from the new structure.

## Best Practices

### 1. Always Use Constructor Injection
```python
# ✅ Good
class WeatherService:
    def __init__(self):
        self.repository = WeatherRepository()

# ❌ Bad
class WeatherService:
    @staticmethod
    def method():
        WeatherRepository.static_method()
```

### 2. Use Base Classes
```python
# ✅ Good
class WeatherRepository(BaseRepository):
    def __init__(self):
        super().__init__("collection_name")

# ❌ Bad
class WeatherRepository:
    def __init__(self):
        self.collection = get_collection()
```

### 3. Use Decorators for Cross-Cutting Concerns
```python
# ✅ Good
@log_execution
@handle_exceptions
async def fetch_weather(self, city: str):
    pass

# ❌ Bad
async def fetch_weather(self, city: str):
    logger.info("Starting...")
    try:
        # code
    except Exception as e:
        logger.error(str(e))
        raise
```

### 4. Use Custom Exceptions
```python
# ✅ Good
if not data:
    raise NotFoundException(f"No data for {city}")

# ❌ Bad
if not data:
    raise Exception(f"No data for {city}")
```

### 5. Keep Layers Separate
```python
# ✅ Good - Controller calls Service
await self.service.get_weather(city)

# ❌ Bad - Controller directly calls Repository
await self.repository.find_one({"city": city})
```

## Future Enhancements

### Possible Improvements
1. **Add Middleware Layer** for authentication, rate limiting
2. **Add DTOs** (Data Transfer Objects) for strict input/output validation
3. **Add Cache Layer** between Service and Repository
4. **Add Event System** for decoupled communication between modules
5. **Add API Versioning** (v1/, v2/) within each module
6. **Add GraphQL Support** alongside REST
7. **Add Unit Tests** for each layer
8. **Add Integration Tests** for full request flow

### Migration to Microservices (Future)
If needed, each feature module (weather/, dashboard/, alerts/) can be extracted into a separate microservice:
```
weather-service/      # Independent service
dashboard-service/    # Independent service
alerts-service/       # Independent service
```

Each would maintain the same internal structure (controller → service → repository).

## Summary

This backend now follows **industry-standard layered architecture** with:
- ✅ Clear separation of concerns
- ✅ Proper OOP principles
- ✅ Dependency injection
- ✅ Reusable base classes
- ✅ Feature-based modules
- ✅ Testable and maintainable code

The architecture is similar to **NestJS**, **Spring Boot**, and **Django** best practices, adapted for Python with FastAPI.
