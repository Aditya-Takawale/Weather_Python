# Weather Monitoring System 🌤️

A modern, full-stack weather monitoring dashboard with real-time data visualization, dual theme support (dark/light), and beautiful responsive UI. Built with FastAPI (Python), React (TypeScript), and MongoDB.

[![GitHub](https://img.shields.io/badge/github-Weather__Python-blue)](https://github.com/Aditya-Takawale/Weather_Python)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## 🌟 Features

- 🌡️ **Real-time Weather Data** - Live temperature, humidity, pressure, wind speed, and more
- 📊 **Interactive Charts** - Hourly temperature bars and 7-day trend visualization
- 🎨 **Dual Theme Support** - Beautiful dark and light themes with smooth transitions and sun/moon slider toggle
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- 🔄 **Auto-refresh** - Automatic data updates every 5 minutes
- 🎭 **Weather Animations** - Dynamic background animations based on weather conditions (rain, snow, clouds, sun, fog)
- 📈 **Historical Data** - 7-day weather history with detailed statistics
- 🎯 **Metric Cards** - Six highlight cards showing key weather metrics with colorful glowing effects
- 🌈 **Production-Ready** - Clean architecture with repository pattern, service layer, and dependency injection

## 🏗️ Project Structure

```
Weather_Python/
├── backend/                      # Backend API server
│   ├── app/                      # Main application code
│   │   ├── api/                  # API routes and endpoints
│   │   │   └── routes/           # Route handlers (dashboard, weather, alerts)
│   │   ├── config/               # Configuration files
│   │   │   ├── database.py       # MongoDB connection
│   │   │   └── settings.py       # App settings
│   │   ├── models/               # Pydantic models
│   │   │   ├── weather.py        # Weather data models
│   │   │   ├── dashboard.py      # Dashboard models
│   │   │   └── alert.py          # Alert models
│   │   ├── repositories/         # Data access layer
│   │   ├── services/             # Business logic layer
│   │   ├── tasks/                # Celery background tasks
│   │   ├── utils/                # Helper functions and utilities
│   │   └── main.py               # FastAPI application entry point
│   ├── scripts/                  # Utility scripts
│   │   ├── populate_data.py              # Fetch current weather data
│   │   ├── populate_historical_data.py   # Generate historical data
│   │   ├── cleanup_other_cities.py       # Database cleanup
│   │   ├── clean_database.py             # Full database reset
│   │   ├── test_connection.py            # Test MongoDB connection
│   │   ├── test_api_simple.py            # API endpoint tests
│   │   └── test_system.py                # System integration tests
│   ├── logs/                     # Application logs
│   ├── .env.example              # Environment variables template
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend Docker configuration
│
├── frontend/                     # React frontend application
│   ├── src/
│   │   ├── api/                  # API client service
│   │   ├── components/           # React components
│   │   │   ├── dashboard/        # Dashboard components
│   │   │   │   ├── TemperatureGauge.tsx     # Circular temperature gauge
│   │   │   │   ├── HourlyBarChart.tsx       # 8-hour temperature chart
│   │   │   │   ├── HighlightCard.tsx        # Metric display cards
│   │   │   │   ├── DailyTrendChart.tsx      # 7-day trend chart
│   │   │   │   └── ...
│   │   │   ├── layout/           # Layout components
│   │   │   │   └── Header.tsx    # Header with theme toggle
│   │   │   └── weather/          # Weather-specific components
│   │   │       └── WeatherAnimation.tsx     # Background animations
│   │   ├── context/              # React Context providers
│   │   │   └── ThemeContext.tsx  # Theme state management
│   │   ├── hooks/                # Custom React hooks
│   │   │   ├── useWeatherData.ts # Weather data fetching
│   │   │   └── useAlerts.ts      # Alert management
│   │   ├── pages/                # Page components
│   │   │   └── Dashboard.tsx     # Main dashboard page
│   │   ├── services/             # API service layer
│   │   ├── types/                # TypeScript type definitions
│   │   ├── theme/                # Material-UI theme configuration
│   │   ├── App.tsx               # Root component
│   │   └── main.tsx              # Application entry point
│   ├── public/                   # Static assets
│   ├── .env.example              # Environment variables template
│   ├── package.json              # Node dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── vite.config.ts            # Vite build configuration
│   └── Dockerfile                # Frontend Docker configuration
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # System architecture details
│   ├── PROJECT_STRUCTURE.md      # Detailed project structure
│   ├── QUICK_START.md            # Quick start guide
│   ├── SETUP.md                  # Setup instructions
│   └── ...                       # Additional documentation
│
├── scripts/                      # Root-level utility scripts
│   ├── setup-dev.ps1             # Development environment setup
│   └── start.ps1                 # Application startup script
│
├── .gitignore                    # Git ignore rules
├── docker-compose.yml            # Docker orchestration
├── package.json                  # Root package configuration
└── README.md                     # This file
```

## 📋 Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18+ and npm
- **MongoDB** 4.4+
- **OpenWeather API Key** - [Get one free here](https://openweathermap.org/api)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Aditya-Takawale/Weather_Python.git
cd Weather_Python
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # On Windows
# source venv/bin/activate     # On Linux/Mac
pip install -r requirements.txt
```

### 3. Configure Environment

Create `backend/.env` file:
```env
OPENWEATHER_API_KEY=your_api_key_here
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=weather_dashboard
LOG_LEVEL=INFO
```

### 4. Populate Data

```bash
# Generate 7 days of historical data
python scripts/populate_historical_data.py

# Fetch current weather data
python scripts/populate_data.py
```

### 5. Start Backend

```bash
set PYTHONPATH=c:\path\to\Weather_Python\backend     # Adjust path as needed
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 7. Start Frontend

```bash
npm run dev
```

### 8. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your OpenWeatherMap API key
# OPENWEATHER_API_KEY=your_api_key_here

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Option B: Manual Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and configure:
# - MongoDB connection string
# - Redis connection string
# - OpenWeatherMap API key

# Start MongoDB (if not already running)
# mongod --dbpath /path/to/data

# Start Redis (if not already running)
# redis-server

# Run database migrations/setup
python -m app.config.database

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# In another terminal, start Celery Beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env if needed (default: VITE_API_URL=http://localhost:8000)

# Start development server
npm run dev
```

### 4. Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
weather_python/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── dashboard.py      # Dashboard endpoints
│   │   │       ├── weather.py        # Weather data endpoints
│   │   │       └── alerts.py         # Alert management endpoints
│   │   ├── config/
│   │   │   ├── settings.py           # Configuration management
│   │   │   └── database.py           # MongoDB connection
│   │   ├── models/
│   │   │   ├── weather.py            # Weather data models
│   │   │   ├── dashboard.py          # Dashboard summary models
│   │   │   └── alert.py              # Alert models
│   │   ├── repositories/
│   │   │   ├── weather_repository.py
│   │   │   ├── dashboard_repository.py
│   │   │   └── alert_repository.py
│   │   ├── services/
│   │   │   ├── weather_service.py
│   │   │   ├── dashboard_service.py
│   │   │   └── alert_service.py
│   │   ├── tasks/
│   │   │   ├── celery_app.py         # Celery configuration
│   │   │   ├── weather_tasks.py      # Weather fetching task
│   │   │   ├── dashboard_tasks.py    # Dashboard aggregation task
│   │   │   ├── cleanup_tasks.py      # Data cleanup task
│   │   │   └── alert_tasks.py        # Alert checking task
│   │   ├── utils/
│   │   │   ├── logger.py             # Logging configuration
│   │   │   └── helpers.py            # Utility functions
│   │   └── main.py                   # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── Header.tsx
│   │   │   └── dashboard/
│   │   │       ├── CurrentWeather.tsx
│   │   │       ├── TodayStats.tsx
│   │   │       ├── HourlyTrendChart.tsx
│   │   │       ├── DailyTrendChart.tsx
│   │   │       ├── WeatherDistribution.tsx
│   │   │       └── AlertsPanel.tsx
│   │   ├── hooks/
│   │   │   ├── useWeatherData.ts
│   │   │   └── useAlerts.ts
│   │   ├── services/
│   │   │   └── api.ts                # API client
│   │   ├── types/
│   │   │   └── weather.types.ts
│   │   ├── theme/
│   │   │   └── theme.ts              # Material-UI theme
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
├── docker-compose.yml
├── ARCHITECTURE.md
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

Edit `backend/.env`:

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=weather_monitoring

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenWeatherMap API
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather

# Default City
DEFAULT_CITY=Pune
DEFAULT_COUNTRY_CODE=IN

# Alert Thresholds
ALERT_HIGH_TEMP_THRESHOLD=35.0
ALERT_LOW_TEMP_THRESHOLD=5.0
ALERT_HIGH_HUMIDITY_THRESHOLD=85.0
ALERT_EXTREME_WEATHER_CONDITIONS=["Thunderstorm","Tornado","Hurricane"]
ALERT_COOLDOWN_MINUTES=60

# Data Retention
DATA_RETENTION_DAYS=2

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Edit `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
```

### Celery Schedule Configuration

Modify schedules in `backend/app/tasks/celery_app.py`:

```python
beat_schedule = {
    'fetch-weather-every-30-minutes': {
        'task': 'app.tasks.weather_tasks.fetch_weather_data',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'populate-dashboard-every-hour': {
        'task': 'app.tasks.dashboard_tasks.populate_dashboard_summary',
        'schedule': crontab(minute=0),  # Every hour
    },
    # ... more tasks
}
```

## 📊 API Endpoints

### Dashboard

- `GET /api/v1/dashboard/summary?city=Pune` - Get pre-aggregated dashboard data
- `POST /api/v1/dashboard/refresh?city=Pune` - Force dashboard refresh
- `GET /api/v1/dashboard/health` - Dashboard health check

### Weather

- `GET /api/v1/weather/current?city=Pune` - Get current weather
- `GET /api/v1/weather/history?city=Pune&hours=24` - Get historical data
- `POST /api/v1/weather/fetch?city=Pune` - Manually trigger weather fetch
- `GET /api/v1/weather/statistics?city=Pune&hours=24` - Get weather statistics

### Alerts

- `GET /api/v1/alerts/active?city=Pune` - Get active alerts
- `GET /api/v1/alerts/recent?city=Pune&hours=24` - Get recent alerts
- `POST /api/v1/alerts/acknowledge/{alert_id}` - Acknowledge an alert
- `GET /api/v1/alerts/statistics?city=Pune&hours=24` - Get alert statistics
- `POST /api/v1/alerts/check?city=Pune` - Manually trigger alert check

### System

- `GET /health` - System health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🗄️ Database Schema

### Collections

#### 1. weather_raw
Stores raw weather data from OpenWeatherMap API.

```javascript
{
  _id: ObjectId,
  city: "Pune",
  country_code: "IN",
  timestamp: ISODate("2024-01-15T10:30:00Z"),
  temperature: 28.5,
  feels_like: 29.2,
  temp_min: 27.0,
  temp_max: 30.0,
  humidity: 65,
  pressure: 1013,
  wind_speed: 5.2,
  wind_direction: 180,
  weather_condition: "Clear",
  weather_description: "clear sky",
  visibility: 10000,
  cloudiness: 20,
  sunrise: ISODate("2024-01-15T06:30:00Z"),
  sunset: ISODate("2024-01-15T18:15:00Z"),
  timezone_offset: 19800,
  is_deleted: false,
  created_at: ISODate("2024-01-15T10:30:00Z")
}
```

**Indexes:**
- `{ city: 1, timestamp: -1 }`
- `{ timestamp: -1 }`
- `{ is_deleted: 1 }`

#### 2. dashboard_summary
Pre-aggregated dashboard data for fast retrieval.

```javascript
{
  _id: ObjectId,
  city: "Pune",
  country_code: "IN",
  generated_at: ISODate("2024-01-15T11:00:00Z"),
  current_weather: { /* CurrentWeather object */ },
  today_stats: {
    temperature: { min: 25.0, max: 32.0, avg: 28.5 },
    humidity: { min: 55, max: 75, avg: 65 },
    pressure: { min: 1010, max: 1015, avg: 1013 },
    wind_speed: { min: 3.0, max: 7.5, avg: 5.2 }
  },
  hourly_trend: [ /* 24 hours of data */ ],
  daily_trend: [ /* 7 days of data */ ],
  weather_distribution: {
    "Clear": 15,
    "Clouds": 8,
    "Rain": 1
  },
  data_quality: {
    total_records: 48,
    missing_records: 0,
    last_update: ISODate("2024-01-15T10:30:00Z")
  }
}
```

**Indexes:**
- `{ city: 1, generated_at: -1 }` (unique)

#### 3. alert_logs
Alert history and management.

```javascript
{
  _id: ObjectId,
  city: "Pune",
  alert_type: "high_temperature",
  severity: "warning",
  message: "High temperature detected: 36.5°C",
  triggered_at: ISODate("2024-01-15T14:30:00Z"),
  is_active: true,
  is_acknowledged: false,
  acknowledged_at: null,
  acknowledged_by: null,
  conditions: {
    current_value: 36.5,
    threshold: 35.0,
    comparison: "greater_than"
  },
  weather_snapshot: { /* Weather data at alert time */ }
}
```

**Indexes:**
- `{ city: 1, triggered_at: -1 }`
- `{ is_active: 1 }`
- `{ alert_type: 1, triggered_at: -1 }`

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_weather_service.py
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## 🐛 Debugging

### View Logs

```bash
# Docker Compose logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Backend logs (manual setup)
tail -f backend/logs/app.log

# Celery worker logs
celery -A app.tasks.celery_app worker --loglevel=debug
```

### Common Issues

**Issue: MongoDB connection refused**
```bash
# Check MongoDB is running
docker ps | grep mongodb
# or
mongosh --eval "db.version()"
```

**Issue: Redis connection refused**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

**Issue: OpenWeatherMap API errors**
- Verify API key is correct
- Check API rate limits (60 calls/minute for free tier)
- Ensure city name is correct

**Issue: Celery tasks not running**
```bash
# Check Celery worker status
celery -A app.tasks.celery_app inspect active

# Check scheduled tasks
celery -A app.tasks.celery_app inspect scheduled

# Restart Celery worker
docker-compose restart celery_worker celery_beat
```

## 📈 Performance Optimization

### Backend
- Pre-aggregated dashboard data updated hourly (reduces real-time computation)
- MongoDB indexes on frequently queried fields
- Async/await for non-blocking I/O operations
- Connection pooling for MongoDB and Redis
- Efficient aggregation pipelines

### Frontend
- React.memo for component memoization
- Lazy loading of heavy components
- Debounced API calls
- Auto-refresh with configurable intervals
- Optimized bundle size with Vite

## 🔒 Security Considerations

- API key stored in environment variables (never committed)
- CORS configured for specific origins
- Input validation with Pydantic
- MongoDB connection with authentication (recommended for production)
- Rate limiting on API endpoints (implement with FastAPI middleware)
- HTTPS in production (configure reverse proxy like Nginx)

## 🚢 Deployment

### Production Checklist

- [ ] Update `.env` with production values
- [ ] Enable MongoDB authentication
- [ ] Configure Redis password
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure CORS for production domain
- [ ] Enable API rate limiting
- [ ] Set up monitoring (e.g., Prometheus + Grafana)
- [ ] Configure logging aggregation (e.g., ELK stack)
- [ ] Set up automated backups for MongoDB
- [ ] Configure health check endpoints
- [ ] Set appropriate resource limits in Docker Compose

### Docker Compose Production

```bash
# Build and start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale workers if needed
docker-compose up -d --scale celery_worker=3
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (to be created).

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

## 🙏 Acknowledgments

- OpenWeatherMap for weather data API
- FastAPI for the excellent web framework
- Material-UI for beautiful React components
- Recharts for data visualization

---

Built with ❤️ using FastAPI, MongoDB, Celery, and React
