# Final Backend Architecture - Layered Design

## Overview

This document describes the **final, production-ready backend architecture** after complete refactoring to Layered Architecture (Clean Architecture) with feature-based modular design.

## Architecture Pattern

**Pattern Name**: **Layered Architecture** (also known as Clean Architecture, Hexagonal Architecture, or Feature-Based Modular Architecture)

**Similar to**: NestJS, Spring Boot, Django Rest Framework, Ruby on Rails

## Complete Directory Structure

```
backend/app/
├── api/                         # Feature modules (business domains)
│   ├── weather/                 # Weather feature module
│   │   ├── tasks/               # Weather-specific background jobs
│   │   │   ├── __init__.py
│   │   │   └── weather_tasks.py
│   │   ├── __init__.py
│   │   ├── weather_repository.py   # Data access layer
│   │   ├── weather_service.py      # Business logic layer
│   │   ├── weather_controller.py   # HTTP handling layer
│   │   └── weather_router.py       # Route definitions
│   │
│   ├── dashboard/               # Dashboard feature module
│   │   ├── tasks/               # Dashboard-specific background jobs
│   │   │   ├── __init__.py
│   │   │   └── dashboard_tasks.py
│   │   ├── __init__.py
│   │   ├── dashboard_repository.py
│   │   ├── dashboard_service.py
│   │   ├── dashboard_controller.py
│   │   └── dashboard_router.py
│   │
│   ├── alerts/                  # Alerts feature module
│   │   ├── tasks/               # Alert-specific background jobs
│   │   │   ├── __init__.py
│   │   │   └── alert_tasks.py
│   │   ├── __init__.py
│   │   ├── alert_repository.py
│   │   ├── alert_service.py
│   │   ├── alert_controller.py
│   │   └── alert_router.py
│   │
│   └── routes/                  # Legacy route aggregation (to be removed)
│       ├── __init__.py          # Aggregates all feature routers
│       ├── weather.py           # DEPRECATED
│       ├── dashboard.py         # DEPRECATED
│       └── alerts.py            # DEPRECATED
│
├── core/                        # Shared infrastructure (cross-cutting concerns)
│   ├── celery/                  # Celery configuration
│   │   ├── __init__.py
│   │   └── celery_app.py        # Celery app, Beat schedule, task routing
│   │
│   ├── logging/                 # Logging utilities
│   │   ├── __init__.py
│   │   └── logger.py            # Logger setup and configuration
│   │
│   ├── tasks/                   # System-level background jobs
│   │   ├── __init__.py
│   │   └── cleanup_tasks.py     # Database cleanup, optimization
│   │
│   ├── utils/                   # Generic helper functions
│   │   ├── __init__.py
│   │   └── helpers.py           # Temperature conversion, formatting, etc.
│   │
│   └── __init__.py              # Core module exports
│
├── common/                      # Base classes and shared components
│   ├── __init__.py
│   ├── base_repository.py       # Generic repository with CRUD operations
│   ├── base_service.py          # Base service with logging
│   ├── base_controller.py       # Base controller with standardized responses
│   ├── exceptions.py            # Custom HTTP exceptions
│   └── decorators.py            # Cross-cutting decorators (error handling, etc.)
│
├── infrastructure/              # External infrastructure (planned)
│   ├── config/                  # Configuration management
│   └── database/                # Database connection and management
│
├── config/                      # Application configuration (current)
│   ├── __init__.py
│   ├── settings.py              # Environment settings, API keys
│   └── database.py              # MongoDB connection manager
│
├── models/                      # Data models (Pydantic schemas)
│   ├── __init__.py
│   ├── weather_model.py
│   ├── dashboard_model.py
│   └── alert_model.py
│
├── tasks/                       # DEPRECATED - moved to feature modules + core
│   └── README.md                # Deprecation notice
│
├── utils/                       # DEPRECATED - moved to core/
│   └── README.md                # Deprecation notice
│
├── repositories/                # DEPRECATED - moved to feature modules
│   └── README.md                # Deprecation notice
│
├── services/                    # DEPRECATED - moved to feature modules
│   └── README.md                # Deprecation notice
│
└── main.py                      # FastAPI application entry point
```

## Request Flow

### HTTP Request Flow
```
HTTP Request
    ↓
Router (weather_router.py) - Route definitions
    ↓
Controller (weather_controller.py) - HTTP handling, validation
    ↓
Service (weather_service.py) - Business logic
    ↓
Repository (weather_repository.py) - Database queries
    ↓
MongoDB
```

### Background Task Flow
```
Celery Beat Scheduler
    ↓
Task (weather_tasks.py) - Background job
    ↓
Service (weather_service.py) - Business logic
    ↓
Repository (weather_repository.py) - Database operations
    ↓
MongoDB
```

## Layer Responsibilities

### 1. Router Layer (`*_router.py`)
- **Purpose**: Define API routes and endpoints
- **Responsibilities**:
  - URL path definitions
  - HTTP method mappings
  - Route-level dependencies
- **Example**:
  ```python
  from fastapi import APIRouter
  from .weather_controller import WeatherController
  
  router = APIRouter(prefix="/weather", tags=["weather"])
  controller = WeatherController()
  
  @router.get("/current/{city}")
  async def get_current(city: str):
      return await controller.get_current_weather(city)
  ```

### 2. Controller Layer (`*_controller.py`)
- **Purpose**: Handle HTTP requests/responses
- **Responsibilities**:
  - Request validation
  - Response formatting
  - Error handling
  - HTTP status codes
- **NO business logic**
- **Example**:
  ```python
  from ..common.base_controller import BaseController
  from .weather_service import WeatherService
  
  class WeatherController(BaseController):
      def __init__(self):
          super().__init__()
          self.service = WeatherService()
      
      async def get_current_weather(self, city: str):
          data = await self.service.get_current_weather(city)
          return self.success_response(data)
  ```

### 3. Service Layer (`*_service.py`)
- **Purpose**: Business logic and orchestration
- **Responsibilities**:
  - Business rules
  - Data validation
  - Orchestrate multiple repositories
  - External API calls
  - Data transformation
- **NO database queries directly**
- **Example**:
  ```python
  from ..common.base_service import BaseService
  from .weather_repository import WeatherRepository
  
  class WeatherService(BaseService):
      def __init__(self):
          super().__init__()
          self.repository = WeatherRepository()
      
      async def get_current_weather(self, city: str):
          # Business logic here
          return await self.repository.get_latest_weather(city)
  ```

### 4. Repository Layer (`*_repository.py`)
- **Purpose**: Data access and persistence
- **Responsibilities**:
  - Database queries
  - CRUD operations
  - Data aggregation
  - Query optimization
- **NO business logic**
- **Example**:
  ```python
  from ..common.base_repository import BaseRepository
  from ..models.weather_model import WeatherData
  
  class WeatherRepository(BaseRepository[WeatherData]):
      def __init__(self):
          super().__init__(
              collection_name="weather_raw",
              model_class=WeatherData
          )
      
      async def get_latest_weather(self, city: str):
          return await self.find_one({"city": city}, sort=[("timestamp", -1)])
  ```

### 5. Task Layer (`tasks/*_tasks.py`)
- **Purpose**: Background job execution
- **Responsibilities**:
  - Scheduled tasks
  - Async job processing
  - Retry logic
  - Task queuing
- **Organized by feature module**
- **Example**:
  ```python
  from ....core.celery import celery_app
  from ..weather_service import WeatherService
  
  @celery_app.task(name="api.weather.tasks.fetch_weather_data")
  def fetch_weather_data(city: str):
      service = WeatherService()
      return asyncio.run(service.fetch_and_store_weather(city))
  ```

## Core Module (`core/`)

### Purpose
Houses **cross-cutting concerns** that are used across multiple features.

### Contents

#### `core/celery/`
- Celery application configuration
- Beat schedule definitions
- Task routing and queue configuration
- Worker settings

#### `core/logging/`
- Centralized logging setup
- Log formatting
- Log level configuration
- File/console handler setup

#### `core/tasks/`
- **System-level tasks** that don't belong to a specific feature
- Examples: database cleanup, optimization, health checks
- Not tied to weather, dashboard, or alerts

#### `core/utils/`
- **Generic utility functions** used across features
- Examples: temperature conversion, date formatting, validation helpers
- Stateless, reusable functions

## Common Module (`common/`)

### Purpose
Shared **base classes** and **abstractions** that feature modules extend.

### Contents

#### `base_repository.py`
- Generic CRUD operations
- Pagination support
- Aggregation helpers
- Type-safe queries using `Generic[T]`

#### `base_service.py`
- Logging helpers
- Validation utilities
- Common service patterns

#### `base_controller.py`
- Standardized response formatting
- Error handling
- Success/error response builders

#### `exceptions.py`
- Custom HTTP exceptions
- Domain-specific errors

#### `decorators.py`
- Cross-cutting decorators
- Error handling, logging, metrics

## Feature Modules (`api/*`)

### Structure
Each feature is **self-contained** with all its layers:

```
api/weather/
├── tasks/                    # Feature-specific background jobs
├── weather_repository.py     # Data access
├── weather_service.py        # Business logic
├── weather_controller.py     # HTTP handling
└── weather_router.py         # Routes
```

### Benefits
1. **Encapsulation**: All weather-related code in one place
2. **Scalability**: Easy to add new features without affecting others
3. **Team Organization**: Different teams can own different features
4. **Testing**: Test entire feature in isolation
5. **Deployment**: Can extract features into microservices later

## Key Architectural Principles

### 1. Dependency Direction
```
Router → Controller → Service → Repository → Database
```
- Each layer only depends on the layer below it
- No circular dependencies
- Lower layers don't know about upper layers

### 2. Dependency Injection
```python
class WeatherController:
    def __init__(self, service: WeatherService = None):
        self.service = service or WeatherService()
```
- Testability: Can inject mock services
- Flexibility: Easy to swap implementations

### 3. Single Responsibility
- Each class has **one reason to change**
- Repository: Database schema changes
- Service: Business logic changes
- Controller: API contract changes

### 4. Open/Closed Principle
- Base classes are **closed for modification**
- Feature modules **extend** base classes
- Add new features without modifying core

### 5. Separation of Concerns
- **Router**: Routes and endpoints
- **Controller**: HTTP protocol
- **Service**: Business logic
- **Repository**: Data persistence
- **Tasks**: Background processing

## Migration from Old Structure

### Old Structure (DEPRECATED)
```
app/
├── tasks/                    # All tasks centralized
│   ├── weather_tasks.py
│   ├── dashboard_tasks.py
│   └── alert_tasks.py
├── utils/                    # All utilities centralized
│   ├── logger.py
│   └── helpers.py
├── services/                 # Static methods
│   └── weather_service.py
└── repositories/             # Static methods
    └── weather_repository.py
```

### New Structure (CURRENT)
```
app/
├── api/
│   └── weather/              # Feature module
│       ├── tasks/            # Feature-specific tasks
│       ├── weather_repository.py  # OOP
│       └── weather_service.py     # OOP
├── core/                     # Shared infrastructure
│   ├── celery/
│   ├── logging/
│   ├── tasks/                # System tasks only
│   └── utils/
└── common/                   # Base classes
```

### Import Migration

**Old:**
```python
from app.tasks.weather_tasks import fetch_weather_data
from app.utils.logger import get_logger
from app.services.weather_service import WeatherService

result = WeatherService.fetch_weather(city)  # Static
```

**New:**
```python
from app.api.weather.tasks import fetch_weather_data
from app.core.logging import get_logger
from app.api.weather.weather_service import WeatherService

service = WeatherService()  # Instance
result = await service.fetch_and_store_weather(city)
```

## Celery Task Organization

### Task Naming Convention
```
<domain>.<feature>.tasks.<task_name>

Examples:
- api.weather.tasks.fetch_weather_data
- api.dashboard.tasks.populate_dashboard_summary
- api.alerts.tasks.check_weather_alerts
- core.tasks.cleanup_old_data
```

### Task Discovery
Celery auto-discovers tasks from:
```python
celery_app.autodiscover_tasks([
    'app.api.weather.tasks',
    'app.api.dashboard.tasks',
    'app.api.alerts.tasks',
    'app.core.tasks'
])
```

### Queue Routing
```python
celery_app.conf.task_routes = {
    'api.weather.tasks.*': {'queue': 'weather_queue'},
    'api.dashboard.tasks.*': {'queue': 'dashboard_queue'},
    'api.alerts.tasks.*': {'queue': 'alert_queue'},
    'core.tasks.*': {'queue': 'maintenance_queue'},
}
```

## Benefits of This Architecture

### 1. **Maintainability**
- Clear separation of concerns
- Easy to locate code
- Self-documenting structure

### 2. **Scalability**
- Add new features without touching existing code
- Independent feature deployment
- Horizontal scaling by feature

### 3. **Testability**
- Mock dependencies easily
- Test each layer independently
- Integration tests per feature

### 4. **Team Collaboration**
- Features owned by different teams
- Minimal merge conflicts
- Clear boundaries

### 5. **Code Reusability**
- Base classes reduce duplication
- Common utilities in core
- Consistent patterns

### 6. **Future-Proof**
- Easy to extract features into microservices
- Support multiple frontends
- Add new channels (GraphQL, gRPC)

## Development Workflow

### Adding a New Feature

1. **Create feature directory**:
   ```
   app/api/notifications/
   ```

2. **Create layers**:
   ```
   ├── tasks/
   │   └── notification_tasks.py
   ├── notification_repository.py
   ├── notification_service.py
   ├── notification_controller.py
   └── notification_router.py
   ```

3. **Extend base classes**:
   ```python
   class NotificationRepository(BaseRepository[Notification]):
       ...
   
   class NotificationService(BaseService):
       ...
   
   class NotificationController(BaseController):
       ...
   ```

4. **Register router**:
   ```python
   # In app/api/routes/__init__.py
   from ..notifications.notification_router import router as notification_router
   ```

5. **Add Celery tasks** (if needed):
   ```python
   @celery_app.task(name="api.notifications.tasks.send_notifications")
   def send_notifications():
       ...
   ```

## Comparison with Other Frameworks

| Framework | Similar To | Pattern |
|-----------|-----------|---------|
| **NestJS** | Modules + Controllers + Services + Repositories | This Architecture |
| **Spring Boot** | Controllers + Services + Repositories + Entities | This Architecture |
| **Django** | Views + Services + Models | Similar |
| **Ruby on Rails** | Controllers + Services + Models | Similar |
| **Laravel** | Controllers + Services + Repositories | This Architecture |

## Conclusion

This architecture provides a **production-grade foundation** for:
- Scalable backend applications
- Team collaboration
- Feature isolation
- Microservice evolution
- Maintenance and testing

All code now follows this pattern consistently, with deprecated folders marked for reference only.

---

**Last Updated**: Current refactoring (tasks/ and utils/ moved to feature modules and core/)
**Status**: ✅ Complete and production-ready
