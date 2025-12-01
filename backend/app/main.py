"""
FastAPI Main Application
Production-grade weather monitoring system API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from .config.settings import settings
from .config.database import DatabaseManager
from .utils.logger import setup_logging, get_logger
from .api.routes import dashboard_router, weather_router, alerts_router

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("[START] Weather Monitoring System API")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    try:
        # Connect to MongoDB
        await DatabaseManager.connect()
        logger.info("[SUCCESS] Database connected successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("[STOP] Shutting down Weather Monitoring System API")
        await DatabaseManager.disconnect()
        logger.info("[SUCCESS] Database disconnected")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 🌤️ Weather Monitoring and Automation System
    
    A production-grade weather monitoring system with:
    - Real-time weather data collection
    - Pre-aggregated dashboard summaries
    - Intelligent alert notifications
    - Historical data analysis
    
    ### Features
    
    * **Dashboard**: Get comprehensive pre-computed weather summaries
    * **Weather**: Access current and historical weather data
    * **Alerts**: Monitor and manage weather alerts
    
    ### Data Collection
    
    - **Source**: OpenWeatherMap API
    - **City**: Pune, India
    - **Frequency**: Every 30 minutes
    - **Retention**: 2 days of detailed data
    
    ### Background Tasks (Celery Beat)
    
    1. **Weather Fetch** (Every 30 min): Collect data from OpenWeatherMap
    2. **Dashboard Population** (Hourly): Aggregate data for fast loading
    3. **Data Cleanup** (Daily): Remove old records
    4. **Alert Checking** (Every 15 min): Monitor conditions and notify
    
    ---
    
    Built with ❤️ using FastAPI, MongoDB, Celery, and React
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(weather_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "🌤️ Weather Monitoring System API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "documentation": "/api/docs",
        "endpoints": {
            "dashboard": f"{settings.API_V1_PREFIX}/dashboard/summary",
            "weather": f"{settings.API_V1_PREFIX}/weather/current",
            "alerts": f"{settings.API_V1_PREFIX}/alerts/active"
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    Checks database connectivity and system status
    """
    try:
        # Check database connection
        db = DatabaseManager.get_database()
        await db.command("ping")
        
        return {
            "status": "healthy",
            "api": "operational",
            "database": "connected",
            "version": settings.APP_VERSION,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "api": "operational",
                "database": "disconnected",
                "error": str(e)
            }
        )


# System info endpoint
@app.get("/info", tags=["System"])
async def system_info():
    """Get system information"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "city": settings.OPENWEATHER_CITY,
        "api_prefix": settings.API_V1_PREFIX,
        "features": {
            "real_time_data": True,
            "dashboard_aggregation": True,
            "weather_alerts": True,
            "historical_data": True
        },
        "schedules": {
            "weather_fetch": "Every 30 minutes",
            "dashboard_update": "Every hour",
            "data_cleanup": "Daily at 2:00 AM",
            "alert_check": "Every 15 minutes"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
