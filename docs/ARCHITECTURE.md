# Weather Monitoring System - Architecture Documentation

## 🏗️ System Overview

A production-grade weather monitoring system with real-time data processing, intelligent alerting, and a high-performance dashboard.

### Technology Stack
- **Backend API**: FastAPI (Python 3.11+)
- **Task Queue**: Celery + Celery Beat
- **Message Broker**: Redis
- **Database**: MongoDB
- **Frontend**: React 18 + Material-UI v5
- **Charts**: Recharts
- **External API**: OpenWeatherMap

---

## 📊 MongoDB Schema Design

### 1. **Raw Weather Data Collection** (`weather_raw`)
```json
{
  "_id": "ObjectId",
  "city": "Pune",
  "timestamp": "ISODate",
  "temperature": {
    "current": 28.5,
    "feels_like": 30.2,
    "min": 25.0,
    "max": 32.0
  },
  "humidity": 65,
  "pressure": 1013,
  "weather": {
    "main": "Clear",
    "description": "clear sky",
    "icon": "01d"
  },
  "wind": {
    "speed": 3.5,
    "deg": 180
  },
  "clouds": 10,
  "visibility": 10000,
  "sunrise": "ISODate",
  "sunset": "ISODate",
  "raw_data": {},
  "created_at": "ISODate",
  "is_deleted": false
}
```

**Indexes:**
- `timestamp` (descending) - for time-based queries
- `city, timestamp` (compound) - for city-specific queries
- `is_deleted` - for cleanup operations
- TTL index on `created_at` (3 days)

---

### 2. **Dashboard Summary Collection** (`dashboard_summary`)
```json
{
  "_id": "ObjectId",
  "city": "Pune",
  "summary_type": "hourly",
  "generated_at": "ISODate",
  "current_weather": {
    "temperature": 28.5,
    "feels_like": 30.2,
    "humidity": 65,
    "pressure": 1013,
    "weather_main": "Clear",
    "weather_description": "clear sky",
    "wind_speed": 3.5
  },
  "today_stats": {
    "temp_avg": 27.8,
    "temp_min": 24.5,
    "temp_max": 31.2,
    "humidity_avg": 62,
    "records_count": 24
  },
  "hourly_trend": [
    {
      "hour": "2025-11-28T10:00:00Z",
      "temperature": 28.5,
      "humidity": 65,
      "weather_main": "Clear"
    }
  ],
  "daily_trend": [
    {
      "date": "2025-11-28",
      "temp_avg": 27.8,
      "temp_min": 24.5,
      "temp_max": 31.2,
      "humidity_avg": 62
    }
  ],
  "weather_distribution": {
    "Clear": 15,
    "Clouds": 7,
    "Rain": 2
  }
}
```

**Indexes:**
- `city, summary_type, generated_at` (compound, descending)

---

### 3. **Alert Logs Collection** (`alert_logs`)
```json
{
  "_id": "ObjectId",
  "city": "Pune",
  "alert_type": "HIGH_TEMPERATURE",
  "severity": "warning",
  "message": "Temperature exceeded 35°C",
  "triggered_at": "ISODate",
  "condition": {
    "threshold_type": "temperature",
    "threshold_value": 35,
    "actual_value": 36.5,
    "operator": ">"
  },
  "is_acknowledged": false,
  "acknowledged_at": null,
  "metadata": {
    "temperature": 36.5,
    "humidity": 70,
    "weather_main": "Hot"
  }
}
```

**Indexes:**
- `city, triggered_at` (compound, descending)
- `is_acknowledged` - for filtering active alerts
- `alert_type` - for alert categorization

---

## 🚀 FastAPI Architecture

### Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py           # Environment config
│   │   └── database.py           # MongoDB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── weather.py            # Weather data models
│   │   ├── dashboard.py          # Dashboard response models
│   │   └── alert.py              # Alert models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── weather_schema.py     # Pydantic schemas
│   │   └── response_schema.py    # API response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_service.py    # Weather API integration
│   │   ├── dashboard_service.py  # Dashboard data logic
│   │   └── alert_service.py      # Alert processing
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── weather_repository.py # Weather DB operations
│   │   ├── dashboard_repository.py
│   │   └── alert_repository.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py      # Dashboard endpoints
│   │   │   ├── weather.py        # Weather endpoints
│   │   │   └── alerts.py         # Alert endpoints
│   │   └── dependencies.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py         # Celery configuration
│   │   ├── weather_tasks.py      # Weather fetching tasks
│   │   ├── dashboard_tasks.py    # Dashboard aggregation
│   │   ├── cleanup_tasks.py      # Data cleanup tasks
│   │   └── alert_tasks.py        # Alert notification tasks
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       └── helpers.py            # Utility functions
├── tests/
├── requirements.txt
└── docker-compose.yml
```

### Key API Endpoints

#### 1. **Dashboard Summary** (Primary)
```
GET /api/v1/dashboard/summary
Response: DashboardSummaryResponse (pre-aggregated data)
- Current weather
- Today's statistics
- Hourly trends (24h)
- Daily trends (7d)
- Weather distribution
```

#### 2. **Active Alerts**
```
GET /api/v1/alerts/active
Response: List[AlertResponse]
```

#### 3. **Historical Data** (Optional)
```
GET /api/v1/weather/history?hours=24
Response: List[WeatherDataResponse]
```

---

## ⚙️ Celery Beat Configuration

### Task Schedule
```python
CELERY_BEAT_SCHEDULE = {
    'fetch-weather-data': {
        'task': 'app.tasks.weather_tasks.fetch_weather_data',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'populate-dashboard-summary': {
        'task': 'app.tasks.dashboard_tasks.populate_dashboard_summary',
        'schedule': crontab(minute=0),  # Every hour
    },
    'cleanup-old-data': {
        'task': 'app.tasks.cleanup_tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'check-weather-alerts': {
        'task': 'app.tasks.alert_tasks.check_weather_alerts',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

### Task Implementations

#### Task 1: Weather Data Fetching (Every 30 min)
- Fetch from OpenWeatherMap API for Pune
- Transform and validate data
- Store in `weather_raw` collection
- Handle API errors gracefully

#### Task 2: Dashboard Data Population (Every hour)
- Query last 24 hours of raw data
- Compute aggregations:
  - Current weather (latest record)
  - Today's min/max/avg (temperature, humidity)
  - Hourly trends (24 data points)
  - Daily trends (7 days)
  - Weather type distribution
- Store in `dashboard_summary` collection
- Keep only latest summary per city

#### Task 3: Data Cleanup (Daily)
- Soft-delete or hard-delete records > 2 days old
- Archive important records (optional)
- Clean up orphaned documents

#### Task 4: Weather Alert Notification (Every 15 min)
- Fetch latest weather data
- Check against thresholds:
  - High Temperature (> 35°C)
  - High Humidity (> 80%)
  - Extreme Weather (Storm, Heavy Rain)
- Create alert log if threshold exceeded
- Send notifications (console log / webhook)
- Prevent duplicate alerts (check recent alerts)

---

## 🎯 Performance Strategy

### 1. **Backend Performance**
- **FastAPI**: Async endpoints for non-blocking I/O
- **MongoDB**: Proper indexing on frequently queried fields
- **Celery**: Background processing offloads heavy computations
- **Pre-aggregation**: Task 2 computes all dashboard data upfront
- **Caching**: Redis for frequently accessed data (optional)

### 2. **Frontend Performance**
- **Optimized Data Payload**: Dashboard receives pre-computed summary (~50KB)
- **React Optimizations**:
  - React.memo for expensive components
  - useMemo/useCallback for computed values
  - Code splitting with React.lazy
- **Efficient Rendering**: Chart data is ready-to-use, no client-side processing
- **Real-time Updates**: Polling every 5 minutes (or WebSocket for live updates)

### 3. **Data Flow**
```
OpenWeatherMap API → [Task 1: Fetch] → MongoDB (Raw)
                                           ↓
                                    [Task 2: Aggregate]
                                           ↓
                                    MongoDB (Summary)
                                           ↓
                                    FastAPI GET /dashboard/summary
                                           ↓
                                    React Dashboard (Instant Load)
```

### 4. **UI/UX Excellence**
- **Material-UI v5**: Modern, accessible components
- **Recharts**: Smooth, interactive charts
- **Responsive Design**: Mobile-first approach
- **Loading States**: Skeleton loaders
- **Error Boundaries**: Graceful error handling
- **Dark Mode**: Optional theme toggle

---

## 🔧 Configuration & Environment

### Environment Variables
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=weather_monitoring

# Redis (Celery Broker)
REDIS_URL=redis://localhost:6379/0

# OpenWeatherMap
OPENWEATHER_API_KEY=your_api_key
OPENWEATHER_CITY=Pune
OPENWEATHER_COUNTRY_CODE=IN

# Alert Thresholds
ALERT_TEMP_HIGH=35
ALERT_HUMIDITY_HIGH=80
ALERT_EXTREME_WEATHER=Storm,Thunderstorm

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

---

## 📦 Deployment

### Docker Compose Services
1. **MongoDB**: Database
2. **Redis**: Message broker
3. **FastAPI**: API server
4. **Celery Worker**: Task executor
5. **Celery Beat**: Task scheduler
6. **React App**: Frontend (production build served via Nginx)

### Production Considerations
- Use MongoDB Atlas for managed database
- Redis Cloud for message broker
- Deploy FastAPI on AWS ECS / Google Cloud Run
- Host React on Vercel / Netlify / S3+CloudFront
- Environment-based configuration
- Proper logging and monitoring (Sentry, CloudWatch)
- API rate limiting and authentication

---

## 🎨 Frontend Component Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Layout.tsx
│   │   ├── dashboard/
│   │   │   ├── CurrentWeather.tsx
│   │   │   ├── TodayStats.tsx
│   │   │   ├── HourlyTrendChart.tsx
│   │   │   ├── DailyTrendChart.tsx
│   │   │   ├── WeatherDistribution.tsx
│   │   │   └── AlertsPanel.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── Card.tsx
│   ├── services/
│   │   └── api.ts
│   ├── hooks/
│   │   ├── useWeatherData.ts
│   │   └── useAlerts.ts
│   ├── types/
│   │   └── weather.types.ts
│   ├── theme/
│   │   └── theme.ts
│   ├── App.tsx
│   └── main.tsx
└── package.json
```

---

## 🚀 Getting Started

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m app.main  # FastAPI
   celery -A app.tasks.celery_app worker -l info
   celery -A app.tasks.celery_app beat -l info
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Docker Setup**
   ```bash
   docker-compose up -d
   ```

This architecture ensures scalability, maintainability, and exceptional performance! 🎯
