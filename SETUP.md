# Python Weather Monitoring System Setup

## 🔑 Your Configuration

### OpenWeatherMap API
- **API Key**: `b369be1b643c9bc1422d0e5d157aa3a8`
- **API URL**: `https://api.openweathermap.org/data/2.5/weather`
- **City**: Pune, India

### MongoDB Database
- **Database Name**: `weather_dashboard`
- **Collections**:
  - `rawweatherdatas` - Raw weather data from API
  - `dashboardsummaries` - Pre-aggregated dashboard data
  - `alertlogs` - Alert history and logs
  - `alertconfigs` - Alert configuration settings

## 🚀 Quick Start

### 1. Install Python Dependencies

```powershell
cd c:\Developer\weather_python\backend
pip install -r requirements.txt
```

### 2. Test Connections

```powershell
# Test MongoDB and OpenWeatherMap API
python test_connection.py
```

This will verify:
- ✅ MongoDB connection
- ✅ OpenWeatherMap API access
- ✅ Existing collections and data

### 3. Start the Backend

**Option A: All-in-One (Windows)**
```powershell
# Open 3 PowerShell terminals:

# Terminal 1: FastAPI Server
cd c:\Developer\weather_python\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
cd c:\Developer\weather_python\backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

# Terminal 3: Celery Beat Scheduler
cd c:\Developer\weather_python\backend
celery -A app.tasks.celery_app beat --loglevel=info
```

**Option B: Docker Compose**
```powershell
cd c:\Developer\weather_python
docker-compose up -d
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Dashboard API**: http://localhost:8000/api/v1/dashboard/summary?city=Pune

## 📊 Using Your Existing Data

The system is configured to work with your existing MongoDB collections:

```python
# Collection names match your database:
rawweatherdatas       # ← Your raw weather data
dashboardsummaries    # ← Pre-computed dashboard data  
alertlogs             # ← Alert history
alertconfigs          # ← Alert configurations
```

## 🧪 Test the API

### Get Dashboard Summary
```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary?city=Pune" | ConvertTo-Json

# Or with curl
curl http://localhost:8000/api/v1/dashboard/summary?city=Pune
```

### Get Current Weather
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/weather/current?city=Pune" | ConvertTo-Json
```

### Get Active Alerts
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/alerts/active?city=Pune" | ConvertTo-Json
```

### Manually Trigger Weather Fetch
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/weather/fetch?city=Pune" -Method Post
```

## 📝 View Existing Data

### Check MongoDB Collections
```powershell
# Open MongoDB Compass and connect to: mongodb://localhost:27017
# Navigate to database: weather_dashboard
# View collections: rawweatherdatas, dashboardsummaries, alertlogs, alertconfigs
```

### Query with mongosh
```bash
mongosh mongodb://localhost:27017/weather_dashboard

# View latest weather data
db.rawweatherdatas.find().sort({timestamp: -1}).limit(5)

# View dashboard summaries
db.dashboardsummaries.find().limit(1)

# View recent alerts
db.alertlogs.find().sort({triggered_at: -1}).limit(10)

# Count documents
db.rawweatherdatas.countDocuments()
db.dashboardsummaries.countDocuments()
db.alertlogs.countDocuments()
```

## 🔄 Celery Tasks (Background Jobs)

The system runs 4 automated tasks:

| Task | Schedule | Description |
|------|----------|-------------|
| **fetch_weather_data** | Every 30 minutes | Fetches current weather from OpenWeatherMap |
| **populate_dashboard_summary** | Every 1 hour | Aggregates data for dashboard |
| **cleanup_old_data** | Daily at 2 AM | Removes old weather records |
| **check_weather_alerts** | Every 15 minutes | Checks for alert conditions |

### Monitor Celery Tasks
```powershell
# View active tasks
celery -A app.tasks.celery_app inspect active

# View scheduled tasks
celery -A app.tasks.celery_app inspect scheduled

# View registered tasks
celery -A app.tasks.celery_app inspect registered
```

## 🎨 Frontend Setup

```powershell
cd c:\Developer\weather_python\frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at: http://localhost:3000
```

## 📊 Data Flow

```
OpenWeatherMap API
       ↓
   (Every 30min)
       ↓
  rawweatherdatas ← Raw weather data stored here
       ↓
   (Every 1 hour)
       ↓
dashboardsummaries ← Pre-aggregated for performance
       ↓
    FastAPI API ← Serves data to frontend
       ↓
  React Dashboard ← Beautiful UI displays data
```

## 🔧 Configuration

### Environment Variables (backend/.env)

```bash
# MongoDB (Your existing database)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=weather_dashboard

# OpenWeatherMap API (Your key)
OPENWEATHER_API_KEY=b369be1b643c9bc1422d0e5d157aa3a8
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
OPENWEATHER_CITY=Pune
OPENWEATHER_COUNTRY_CODE=IN
OPENWEATHER_UNITS=metric

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Alert Thresholds
ALERT_TEMP_HIGH=35.0
ALERT_TEMP_LOW=5.0
ALERT_HUMIDITY_HIGH=80.0
```

## 🐛 Troubleshooting

### MongoDB Connection Issues
```powershell
# Check if MongoDB is running
Get-Process mongod

# Or check with test script
python test_connection.py
```

### Redis Not Running
```powershell
# Install Redis for Windows or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Celery on Windows
Windows requires the `--pool=solo` option:
```powershell
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

### API Key Issues
If you get 401 errors, verify your API key:
```powershell
curl "https://api.openweathermap.org/data/2.5/weather?q=Pune&appid=b369be1b643c9bc1422d0e5d157aa3a8&units=metric"
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Next Steps

1. ✅ **Test connection**: `python test_connection.py`
2. ✅ **Start backend**: Three terminals (API, Worker, Beat)
3. ✅ **Test API**: Visit http://localhost:8000/docs
4. ✅ **Start frontend**: `cd frontend && npm run dev`
5. ✅ **View dashboard**: http://localhost:3000

---

**Ready to go!** 🚀 Your Python project is configured to work with your existing `weather_dashboard` MongoDB database.
