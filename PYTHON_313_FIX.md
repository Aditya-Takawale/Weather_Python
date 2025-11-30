# Weather Monitoring System - Python 3.13 Compatibility Guide

## ⚠️ Python 3.13 Compatibility Issue

You're running **Python 3.13.7**, which is very new and has compatibility issues with some packages (especially `pydantic-core` which requires Rust compilation).

## 🔧 Solution Options

### Option 1: Use Docker (Recommended - Easiest)

Docker will handle all dependencies automatically:

```powershell
# Navigate to project root
cd c:\Developer\weather_python

# Start all services (uses Python 3.11 in container)
docker-compose up -d

# View logs
docker-compose logs -f

# Access:
# API: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### Option 2: Install Python 3.11 (Recommended for Development)

1. Download Python 3.11: https://www.python.org/downloads/release/python-31110/
2. Install alongside Python 3.13
3. Use `py -3.11` to run Python 3.11 specifically

```powershell
# Create virtual environment with Python 3.11
py -3.11 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

### Option 3: Try Pre-built Wheels (May Not Work)

```powershell
# Try installing with pre-built wheels
pip install --only-binary :all: pydantic pydantic-core

# If that fails, install older compatible versions
pip install pydantic==2.5.0 pydantic-core==2.14.5
```

### Option 4: Downgrade Python 3.13 → 3.11

Uninstall Python 3.13 and install Python 3.11.9:
- Python 3.11.9: https://www.python.org/downloads/release/python-3119/

## 🐳 Quick Start with Docker (Simplest)

This avoids all Python version issues:

```powershell
# 1. Make sure Docker Desktop is running

# 2. Navigate to project
cd c:\Developer\weather_python

# 3. Start everything
docker-compose up -d

# 4. Wait ~30 seconds for services to start

# 5. Check status
docker-compose ps

# 6. View logs
docker-compose logs -f api

# 7. Access API
# http://localhost:8000/docs
```

## 📋 What Each Service Does

```
┌─────────────────────────────────────┐
│  MongoDB (Port 27017)               │ ← Your existing database
│  - Database: weather_dashboard      │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Redis (Port 6379)                  │ ← Message broker
│  - For Celery task queue            │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  FastAPI (Port 8000)                │ ← REST API
│  - Python 3.11 in container         │
│  - Auto-reloads on code changes     │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Celery Worker                      │ ← Background tasks
│  - Weather fetching                 │
│  - Dashboard aggregation            │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Celery Beat                        │ ← Task scheduler
│  - Runs tasks on schedule           │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  React Frontend (Port 3000)         │ ← Dashboard UI
│  - Beautiful Material-UI dashboard  │
└─────────────────────────────────────┘
```

## 🧪 Test Docker Setup

```powershell
# Check all services are running
docker-compose ps

# Should show:
# weather_mongodb    running
# weather_redis      running
# weather_api        running
# weather_worker     running
# weather_beat       running
# weather_frontend   running

# Test API
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Test Weather Endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary?city=Pune"
```

## 🛠️ Docker Commands

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart api

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f api
docker-compose logs -f celery_worker

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

## 🔍 Troubleshooting Docker

### Docker Desktop Not Running
```powershell
# Check if Docker is running
docker info

# If error, start Docker Desktop app
```

### Port Already in Use
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <process_id> /F
```

### Container Won't Start
```powershell
# View detailed logs
docker-compose logs api

# Check container status
docker ps -a

# Remove and recreate
docker-compose down
docker-compose up -d --force-recreate
```

## 💡 Recommended Approach

**For Development**: Use Docker (easiest, no Python version issues)
**For Production**: Also use Docker (consistent environment)

### Why Docker is Better Here:

1. ✅ No Python version conflicts
2. ✅ All services configured correctly
3. ✅ One command to start everything
4. ✅ Same environment as production
5. ✅ Easy to share with team
6. ✅ MongoDB and Redis included

## 🚀 Full Docker Workflow

```powershell
# 1. Start Docker Desktop

# 2. Navigate to project
cd c:\Developer\weather_python

# 3. Build and start all services
docker-compose up -d --build

# 4. Wait 30 seconds for initialization

# 5. Check everything is running
docker-compose ps

# 6. Test API
start http://localhost:8000/docs

# 7. Test Dashboard (after it builds)
start http://localhost:3000

# 8. View real-time logs
docker-compose logs -f

# When done:
# Stop: docker-compose stop
# Remove: docker-compose down
```

## 📝 Alternative: Python 3.11 Virtual Environment

If you don't want Docker:

```powershell
# 1. Install Python 3.11 from python.org

# 2. Create venv with Python 3.11
py -3.11 -m venv venv311

# 3. Activate
.\venv311\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start services (3 terminals)
# Terminal 1:
uvicorn app.main:app --reload

# Terminal 2:
celery -A app.tasks.celery_app worker -l info --pool=solo

# Terminal 3:
celery -A app.tasks.celery_app beat -l info
```

## ✅ Best Solution Summary

**Use Docker Compose** - It's already configured and will work perfectly:

```powershell
cd c:\Developer\weather_python
docker-compose up -d
```

That's it! Everything will work.

---

**Need help?** Check the logs:
```powershell
docker-compose logs -f
```
