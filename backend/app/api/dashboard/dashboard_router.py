"""
Dashboard API Router
FastAPI routes for dashboard endpoints
"""

from fastapi import APIRouter
from typing import Optional

from .dashboard_controller import DashboardController

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Initialize controller
dashboard_controller = DashboardController()


@router.get(
    "/summary",
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
    return await dashboard_controller.get_dashboard_summary(city)


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
    return await dashboard_controller.trigger_dashboard_refresh(city)
