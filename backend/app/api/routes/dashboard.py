"""
Dashboard API Routes
Primary endpoint for serving pre-aggregated dashboard data
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from datetime import datetime

from ...models.dashboard import DashboardSummaryResponse, DashboardSummary
from ...services.dashboard_service import DashboardService
from ...utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get Dashboard Summary",
    description="""
    Get comprehensive pre-aggregated dashboard summary data.
    
    This endpoint provides:
    - Current weather snapshot
    - Today's statistics (min, max, avg)
    - Hourly trend (last 24 hours)
    - Daily trend (last 7 days)
    - Weather distribution
    
    Data is pre-computed every hour by Celery for optimal performance.
    """
)
async def get_dashboard_summary(city: Optional[str] = "Pune"):
    """
    **PRIMARY DASHBOARD ENDPOINT**
    
    Returns pre-aggregated summary data optimized for instant loading.
    All computations are done server-side by Celery tasks.
    
    Args:
        city: City name (default: Pune)
        
    Returns:
        DashboardSummaryResponse with complete dashboard data
    """
    try:
        logger.info(f"Dashboard summary requested for {city}")
        
        # Get latest pre-computed summary from database
        summary_data = await DashboardService.get_latest_dashboard_summary(city)
        
        if not summary_data:
            logger.warning(f"No dashboard summary found for {city}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No dashboard data available for {city}. Please wait for data collection."
            )
        
        # Convert to response model
        summary = DashboardSummary(**summary_data)
        
        response = DashboardSummaryResponse(
            success=True,
            data=summary,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Dashboard summary served for {city}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )


@router.post(
    "/refresh",
    summary="Trigger Dashboard Refresh",
    description="Manually trigger dashboard summary regeneration"
)
async def trigger_dashboard_refresh(city: Optional[str] = "Pune"):
    """
    Manually trigger dashboard summary regeneration.
    Useful for immediate updates or troubleshooting.
    
    Args:
        city: City name
        
    Returns:
        Status message
    """
    try:
        logger.info(f"Manual dashboard refresh triggered for {city}")
        
        # Generate new summary
        summary = await DashboardService.generate_dashboard_summary(city)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No weather data available for {city}"
            )
        
        # Save summary
        await DashboardService.save_dashboard_summary(summary)
        
        return {
            "success": True,
            "message": f"Dashboard summary refreshed for {city}",
            "generated_at": summary.generated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh dashboard summary"
        )


@router.get(
    "/health",
    summary="Dashboard Health Check",
    description="Check if dashboard data is up-to-date"
)
async def dashboard_health(city: Optional[str] = "Pune"):
    """
    Check dashboard data health and freshness.
    
    Args:
        city: City name
        
    Returns:
        Health status information
    """
    try:
        summary_data = await DashboardService.get_latest_dashboard_summary(city)
        
        if not summary_data:
            return {
                "status": "no_data",
                "message": f"No dashboard data available for {city}",
                "healthy": False
            }
        
        generated_at = summary_data.get("generated_at")
        age_minutes = (datetime.utcnow() - generated_at).total_seconds() / 60 if generated_at else None
        
        # Consider data stale if older than 90 minutes (should update hourly)
        is_fresh = age_minutes < 90 if age_minutes else False
        
        return {
            "status": "healthy" if is_fresh else "stale",
            "message": "Dashboard data is up-to-date" if is_fresh else "Dashboard data may be outdated",
            "healthy": is_fresh,
            "city": city,
            "generated_at": generated_at,
            "age_minutes": round(age_minutes, 1) if age_minutes else None,
            "records_count": summary_data.get("today_stats", {}).get("records_count", 0)
        }
        
    except Exception as e:
        logger.error(f"Error checking dashboard health: {e}")
        return {
            "status": "error",
            "message": str(e),
            "healthy": False
        }
