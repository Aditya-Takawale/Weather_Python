# Backend Architecture Visual Guide

## 🏗️ Complete Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND APPLICATION                          │
│                   (FastAPI + Celery + MongoDB)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼────────┐            ┌────────▼───────┐
        │   HTTP API     │            │  Celery Worker │
        │   (FastAPI)    │            │  (Background)  │
        └───────┬────────┘            └────────┬───────┘
                │                               │
                │                               │
┌───────────────┴───────────────────────────────┴────────────────┐
│                      FEATURE MODULES (api/)                     │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │    Weather      │  │   Dashboard     │  │     Alerts     │ │
│  │    Module       │  │     Module      │  │     Module     │ │
│  ├─────────────────┤  ├─────────────────┤  ├────────────────┤ │
│  │ • Router        │  │ • Router        │  │ • Router       │ │
│  │ • Controller    │  │ • Controller    │  │ • Controller   │ │
│  │ • Service       │  │ • Service       │  │ • Service      │ │
│  │ • Repository    │  │ • Repository    │  │ • Repository   │ │
│  │ • Tasks         │  │ • Tasks         │  │ • Tasks        │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────────┬─┘
                                                                │
                        ┌───────────────────────────────────────┘
                        │
            ┌───────────┴────────────┬─────────────────┐
            │                        │                  │
    ┌───────▼────────┐      ┌───────▼────────┐  ┌─────▼──────┐
    │  CORE (core/)  │      │ COMMON         │  │ INFRA      │
    │                │      │ (common/)      │  │ (config/)  │
    ├────────────────┤      ├────────────────┤  ├────────────┤
    │ • Celery       │      │ • Base Classes │  │ • Settings │
    │ • Logging      │      │ • Exceptions   │  │ • Database │
    │ • Utilities    │      │ • Decorators   │  └────────────┘
    │ • System Tasks │      └────────────────┘
    └────────────────┘
            │
            │
    ┌───────▼────────┐
    │    MongoDB     │
    │   (Database)   │
    └────────────────┘
```

## 📊 Request Flow Diagram

### HTTP Request Flow
```
   Client (Browser/API)
          │
          ▼
   ┌────────────────┐
   │  FastAPI App   │
   │    (main.py)   │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐
   │  Router Layer  │  ← Define routes: /weather, /dashboard, /alerts
   │ weather_router │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐
   │ Controller     │  ← Handle HTTP: request/response formatting
   │ WeatherCtrl    │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐
   │  Service       │  ← Business logic: validation, orchestration
   │ WeatherService │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐
   │  Repository    │  ← Database queries: CRUD operations
   │ WeatherRepo    │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐
   │    MongoDB     │  ← Data storage
   └────────────────┘
```

### Celery Task Flow
```
   Celery Beat Scheduler
          │
          ▼
   ┌─────────────────┐
   │   Task Layer    │  ← Background jobs
   │ weather_tasks   │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  Service Layer  │  ← Business logic
   │ WeatherService  │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ Repository      │  ← Database queries
   │ WeatherRepo     │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │    MongoDB      │  ← Data storage
   └─────────────────┘
```

## 🗂️ Feature Module Structure

### Weather Module (api/weather/)
```
weather/
├── tasks/
│   ├── __init__.py
│   └── weather_tasks.py          ← Background: Fetch weather every 10 min
│
├── __init__.py
├── weather_repository.py         ← Data Access: CRUD operations
├── weather_service.py            ← Business Logic: API calls, validation
├── weather_controller.py         ← HTTP Handling: Request/response
└── weather_router.py             ← Routes: /weather/* endpoints

Request Flow:
Router → Controller → Service → Repository → MongoDB
```

### Dashboard Module (api/dashboard/)
```
dashboard/
├── tasks/
│   ├── __init__.py
│   └── dashboard_tasks.py        ← Background: Aggregate data hourly
│
├── __init__.py
├── dashboard_repository.py       ← Data Access: Summary queries
├── dashboard_service.py          ← Business Logic: Aggregation, stats
├── dashboard_controller.py       ← HTTP Handling: Dashboard API
└── dashboard_router.py           ← Routes: /dashboard/* endpoints
```

### Alerts Module (api/alerts/)
```
alerts/
├── tasks/
│   ├── __init__.py
│   └── alert_tasks.py            ← Background: Check alerts every 15 min
│
├── __init__.py
├── alert_repository.py           ← Data Access: Alert logs
├── alert_service.py              ← Business Logic: Threshold checks
├── alert_controller.py           ← HTTP Handling: Alert API
└── alert_router.py               ← Routes: /alerts/* endpoints
```

## 🔧 Core Infrastructure (core/)

```
core/
├── celery/                       ← Celery Configuration
│   ├── __init__.py
│   └── celery_app.py             • Beat scheduler
│                                 • Task discovery
│                                 • Queue routing
│
├── logging/                      ← Logging Utilities
│   ├── __init__.py
│   └── logger.py                 • Logger setup
│                                 • Log formatting
│                                 • Console/file handlers
│
├── tasks/                        ← System-Level Tasks
│   ├── __init__.py
│   └── cleanup_tasks.py          • Database cleanup
│                                 • Maintenance jobs
│                                 • Health checks
│
├── utils/                        ← Generic Utilities
│   ├── __init__.py
│   └── helpers.py                • Temperature conversion
│                                 • Date formatting
│                                 • Validation helpers
│
└── __init__.py                   ← Core exports
```

## 🏛️ Common Base Classes (common/)

```
common/
├── __init__.py
│
├── base_repository.py            ← Generic Repository<T>
│   • find_one(), find_many()
│   • insert_one(), insert_many()
│   • update_one(), delete_one()
│   • count(), aggregate()
│
├── base_service.py               ← Base Service
│   • Logging helpers
│   • Validation utilities
│   • Common patterns
│
├── base_controller.py            ← Base Controller
│   • success_response()
│   • error_response()
│   • handle_exception()
│
├── exceptions.py                 ← Custom Exceptions
│   • BadRequestException (400)
│   • NotFoundException (404)
│   • ValidationException (422)
│   • InternalServerError (500)
│
└── decorators.py                 ← Cross-Cutting Decorators
    • @error_handler
    • @log_execution
    • @validate_input
```

## 🔄 Dependency Flow

```
┌──────────────────────────────────────────────┐
│         DEPENDENCY DIRECTION                 │
│                                              │
│   Top (Depends on everything below)          │
│         ↓                                    │
│   ┌─────────────────┐                       │
│   │    Router       │  (Depends on Controller)
│   └────────┬────────┘                       │
│            ↓                                 │
│   ┌─────────────────┐                       │
│   │   Controller    │  (Depends on Service)  │
│   └────────┬────────┘                       │
│            ↓                                 │
│   ┌─────────────────┐                       │
│   │    Service      │  (Depends on Repository)│
│   └────────┬────────┘                       │
│            ↓                                 │
│   ┌─────────────────┐                       │
│   │   Repository    │  (Depends on Database) │
│   └────────┬────────┘                       │
│            ↓                                 │
│   ┌─────────────────┐                       │
│   │    Database     │  (No dependencies)    │
│   └─────────────────┘                       │
│         ↑                                    │
│   Bottom (Pure infrastructure)               │
│                                              │
│  Lower layers DON'T know about upper layers │
└──────────────────────────────────────────────┘
```

## 📦 Task Organization

### Task Naming Convention
```
<domain>.<feature>.tasks.<task_name>

Feature Tasks:
┌──────────────────────────────────────────────┐
│ api.weather.tasks.fetch_weather_data        │  ← Weather feature
│ api.weather.tasks.fetch_on_demand           │
├──────────────────────────────────────────────┤
│ api.dashboard.tasks.populate_summary        │  ← Dashboard feature
│ api.dashboard.tasks.generate_on_demand      │
├──────────────────────────────────────────────┤
│ api.alerts.tasks.check_weather_alerts       │  ← Alerts feature
│ api.alerts.tasks.send_alert_digest          │
└──────────────────────────────────────────────┘

System Tasks:
┌──────────────────────────────────────────────┐
│ core.tasks.cleanup_old_data                 │  ← System-level
│ core.tasks.hard_delete_old_data             │
│ core.tasks.cleanup_old_alerts               │
│ core.tasks.optimize_database                │
└──────────────────────────────────────────────┘
```

### Task Queues
```
┌──────────────────┐     ┌──────────────────┐
│ weather_queue    │     │ dashboard_queue  │
├──────────────────┤     ├──────────────────┤
│ • fetch_weather  │     │ • populate_dash  │
│ • fetch_on_demand│     │ • generate_dash  │
└──────────────────┘     └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ alert_queue      │     │ maintenance_queue│
├──────────────────┤     ├──────────────────┤
│ • check_alerts   │     │ • cleanup_data   │
│ • send_digest    │     │ • optimize_db    │
└──────────────────┘     └──────────────────┘
```

## 🎯 Key Principles

### 1. Single Responsibility
```
┌─────────────────────────────────────────┐
│ Each layer has ONE reason to change:   │
│                                         │
│ Router     → Route definitions change   │
│ Controller → API contract changes       │
│ Service    → Business rules change      │
│ Repository → Database schema changes    │
└─────────────────────────────────────────┘
```

### 2. Dependency Injection
```python
# Service depends on Repository
class WeatherService(BaseService):
    def __init__(self, repository: WeatherRepository = None):
        self.repository = repository or WeatherRepository()

# Controller depends on Service
class WeatherController(BaseController):
    def __init__(self, service: WeatherService = None):
        self.service = service or WeatherService()
```

### 3. Feature Isolation
```
┌───────────────────────────────────────────┐
│ Each feature module is independent:      │
│                                           │
│ api/weather/    ← Weather domain         │
│ api/dashboard/  ← Dashboard domain        │
│ api/alerts/     ← Alerts domain           │
│                                           │
│ Can be developed, tested, and deployed    │
│ independently without affecting others    │
└───────────────────────────────────────────┘
```

## 📈 Scalability Path

### Current: Modular Monolith
```
┌─────────────────────────────────────┐
│         Single Application          │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │ Weather  │  │Dashboard │       │
│  │  Module  │  │  Module  │  ...  │
│  └──────────┘  └──────────┘       │
│                                     │
│        Shared Database              │
└─────────────────────────────────────┘
```

### Future: Microservices
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Weather    │  │  Dashboard   │  │   Alerts     │
│   Service    │  │   Service    │  │   Service    │
│              │  │              │  │              │
│   ┌──────┐   │  │   ┌──────┐   │  │   ┌──────┐   │
│   │  DB  │   │  │   │  DB  │   │  │   │  DB  │   │
│   └──────┘   │  │   └──────┘   │  │   └──────┘   │
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                  ↓                  ↓
       └──────────────────┴──────────────────┘
                          │
                    API Gateway
```

## ✅ Architecture Checklist

```
✅ Clear separation of concerns (Router, Controller, Service, Repository)
✅ Feature-based modular design (Weather, Dashboard, Alerts)
✅ DRY principle (Base classes in common/)
✅ Dependency injection (Constructor injection)
✅ Single responsibility (Each layer has one job)
✅ Dependency inversion (Depend on abstractions)
✅ Open/closed principle (Extend, don't modify)
✅ Task organization (Feature tasks + System tasks)
✅ Code reusability (Core utilities, Common base classes)
✅ Testability (Each layer can be tested independently)
✅ Scalability (Can evolve to microservices)
✅ Maintainability (Easy to locate and update code)
```

---

**Pattern**: Layered Architecture (Clean Architecture)  
**Similar to**: NestJS, Spring Boot, Django Rest Framework  
**Status**: ✅ Production-Ready
