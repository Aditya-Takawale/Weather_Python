# Quick Reference Guide

## 🚀 Quick Start Commands

### Using Docker (Recommended)
```powershell
# First time setup
.\start.ps1

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart api
docker-compose restart celery_worker
```

### Manual Development Setup
```powershell
# One-time setup
.\setup-dev.ps1

# Start MongoDB
mongod --dbpath C:\data\db

# Start Redis
redis-server

# Terminal 1: FastAPI
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Celery Beat
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app beat --loglevel=info

# Terminal 4: React Frontend
cd frontend
npm run dev
```

## 📊 API Endpoints Quick Reference

### Dashboard
- `GET /api/v1/dashboard/summary?city=Pune` - Main dashboard data
- `POST /api/v1/dashboard/refresh?city=Pune` - Force refresh
- `GET /api/v1/dashboard/health` - Health check

### Weather
- `GET /api/v1/weather/current?city=Pune` - Current weather
- `GET /api/v1/weather/history?city=Pune&hours=24` - Historical data
- `POST /api/v1/weather/fetch?city=Pune` - Manual fetch
- `GET /api/v1/weather/statistics?city=Pune` - Statistics

### Alerts
- `GET /api/v1/alerts/active?city=Pune` - Active alerts
- `GET /api/v1/alerts/recent?city=Pune&hours=24` - Recent alerts
- `POST /api/v1/alerts/acknowledge/{alert_id}` - Acknowledge alert
- `GET /api/v1/alerts/statistics?city=Pune` - Alert statistics

### System
- `GET /health` - System health
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc UI

## 🔧 Common Tasks

### Update Environment Variables
```powershell
# Backend
notepad backend\.env

# Frontend
notepad frontend\.env

# Restart services after changes
docker-compose restart
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
docker-compose logs -f mongodb
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100
```

### Database Operations
```powershell
# Access MongoDB shell
docker-compose exec mongodb mongosh

# In MongoDB shell:
use weather_monitoring
db.weather_raw.find().limit(5)
db.dashboard_summary.find().limit(1)
db.alert_logs.find()

# Backup database
docker-compose exec mongodb mongodump --out /backup

# Restore database
docker-compose exec mongodb mongorestore /backup
```

### Redis Operations
```powershell
# Access Redis CLI
docker-compose exec redis redis-cli

# In Redis CLI:
PING                    # Should return PONG
KEYS *                  # List all keys
GET celery-task-meta-*  # View task results
FLUSHDB                 # Clear all keys (use with caution!)
```

### Celery Operations
```powershell
# View active tasks
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active

# View scheduled tasks
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect scheduled

# Purge all tasks
docker-compose exec celery_worker celery -A app.tasks.celery_app purge

# View registered tasks
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect registered
```

### Testing
```powershell
# Run system tests
cd backend
.\venv\Scripts\Activate.ps1
python test_system.py

# Test API manually with curl
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/dashboard/summary?city=Pune

# Or use PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/health"
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary?city=Pune"
```

### Debugging

#### Check Service Status
```powershell
docker-compose ps
```

#### Check Container Resource Usage
```powershell
docker stats
```

#### Restart Stuck Service
```powershell
docker-compose restart celery_worker
```

#### View Service Configuration
```powershell
docker-compose config
```

#### Access Container Shell
```powershell
docker-compose exec api /bin/bash
docker-compose exec mongodb mongosh
```

## 🐛 Troubleshooting

### MongoDB Connection Issues
```powershell
# Check if MongoDB is running
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb

# Test connection
docker-compose exec mongodb mongosh --eval "db.version()"
```

### Redis Connection Issues
```powershell
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli PING

# Restart Redis
docker-compose restart redis
```

### Celery Tasks Not Running
```powershell
# Check worker status
docker-compose ps celery_worker celery_beat

# View worker logs
docker-compose logs celery_worker
docker-compose logs celery_beat

# Restart workers
docker-compose restart celery_worker celery_beat

# Check if tasks are registered
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect registered
```

### Frontend Not Loading
```powershell
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend

# Check if API is accessible
curl http://localhost:8000/health
```

### OpenWeatherMap API Issues
```powershell
# Check API key in .env
cat .env | Select-String "OPENWEATHER_API_KEY"

# Test API manually
curl "https://api.openweathermap.org/data/2.5/weather?q=Pune,IN&appid=YOUR_API_KEY&units=metric"

# View weather fetch logs
docker-compose logs celery_worker | Select-String "weather"
```

## 📈 Monitoring

### Check System Health
```powershell
# API health
curl http://localhost:8000/health

# Dashboard health
curl http://localhost:8000/api/v1/dashboard/health

# All services
docker-compose ps
```

### View Performance Metrics
```powershell
# Container resource usage
docker stats

# MongoDB stats
docker-compose exec mongodb mongosh --eval "db.stats()"

# Collection sizes
docker-compose exec mongodb mongosh weather_monitoring --eval "
  db.weather_raw.stats().size;
  db.dashboard_summary.stats().size;
  db.alert_logs.stats().size;
"
```

## 🔄 Updates and Maintenance

### Update Dependencies
```powershell
# Backend
cd backend
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update

# Rebuild containers
docker-compose build
docker-compose up -d
```

### Clean Up Old Data
```powershell
# Prune Docker resources
docker system prune -a --volumes

# Clean MongoDB data (run cleanup task manually)
curl -X POST http://localhost:8000/api/v1/weather/cleanup
```

### Backup Data
```powershell
# Backup MongoDB
docker-compose exec mongodb mongodump --out /backup --db weather_monitoring

# Copy backup from container
docker cp $(docker-compose ps -q mongodb):/backup ./mongodb-backup

# Backup .env files
Copy-Item backend\.env backend\.env.backup
Copy-Item frontend\.env frontend\.env.backup
```

## 📝 Development Workflow

### Make Changes to Backend
```powershell
# 1. Edit code in backend/app/
# 2. If using Docker, changes auto-reload
# 3. If not, restart uvicorn

# 4. Test changes
curl http://localhost:8000/docs
```

### Make Changes to Frontend
```powershell
# 1. Edit code in frontend/src/
# 2. Vite will auto-reload
# 3. Check browser console for errors
```

### Add New Dependencies

#### Python
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install package-name
pip freeze > requirements.txt
```

#### Node.js
```powershell
cd frontend
npm install package-name
npm install --save-dev package-name  # for dev dependencies
```

### Run Tests
```powershell
# Backend
cd backend
.\venv\Scripts\Activate.ps1
pytest

# Frontend
cd frontend
npm test
```

## 🎯 Useful URLs

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **MongoDB**: mongodb://localhost:27017 (if using external client)
- **Redis**: redis://localhost:6379 (if using external client)

## 💡 Tips

1. **Always check logs first** when debugging: `docker-compose logs -f`
2. **Use API docs** for testing endpoints: http://localhost:8000/docs
3. **Monitor Celery Beat** to see when tasks run: `docker-compose logs celery_beat`
4. **Check MongoDB indexes** if queries are slow: `db.collection.getIndexes()`
5. **Use Redis CLI** to debug task issues: `docker-compose exec redis redis-cli`
6. **Enable debug logging** by setting `LOG_LEVEL=DEBUG` in .env
7. **Check Docker resource usage** if things are slow: `docker stats`

## 📞 Getting Help

1. Check the main [README.md](README.md) for comprehensive documentation
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
3. Check API documentation at http://localhost:8000/docs
4. View logs for error messages: `docker-compose logs -f`
5. Run system tests: `python backend/test_system.py`

---

**Last Updated**: 2024
**Version**: 1.0.0
