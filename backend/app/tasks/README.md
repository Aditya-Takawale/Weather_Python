# DEPRECATED - Legacy Code

This folder contains the old static-method architecture and is **NO LONGER USED** by the application.

## Current Architecture

The application now uses **Layered Architecture (Clean Architecture)** with feature-based modules:

```
backend/app/
├── api/
│   ├── weather/         # Weather feature module
│   │   ├── tasks/       # Weather-specific background jobs
│   │   ├── weather_repository.py
│   │   ├── weather_service.py
│   │   ├── weather_controller.py
│   │   └── weather_router.py
│   ├── dashboard/       # Dashboard feature module
│   └── alerts/          # Alerts feature module
├── core/                # Shared infrastructure
│   ├── celery/          # Celery configuration
│   ├── logging/         # Logging utilities
│   ├── tasks/           # System-level tasks
│   └── utils/           # Helper functions
├── common/              # Base classes
└── infrastructure/      # Database, config
```

## This Folder is DEPRECATED

All code in this folder has been refactored and moved to the appropriate feature modules.

**DO NOT use imports from this folder.**

See `ARCHITECTURE_PATTERN.md` for the full architecture documentation.
