"""
Alerts API Router
FastAPI routes for alert endpoints
"""

from fastapi import APIRouter, Query
from typing import Optional

from ...models.alert import AlertAcknowledgeRequest
from .alert_controller import AlertController

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Initialize controller
alert_controller = AlertController()


@router.get(
    "/active",
    summary="Get Active Alerts",
    description="Get all unacknowledged weather alerts"
)
async def get_active_alerts(
    city: Optional[str] = None,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of alerts to return"
    )
):
    """
    Get active (unacknowledged) weather alerts.
    
    Args:
        city: Filter by city (optional)
        limit: Maximum number of alerts
        
    Returns:
        List of active alerts
    """
    return await alert_controller.get_active_alerts(city, limit)


@router.get(
    "/recent",
    summary="Get Recent Alerts",
    description="Get recent weather alerts within specified time range"
)
async def get_recent_alerts(
    city: Optional[str] = None,
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Hours of history (max 7 days)"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
        description="Maximum number of alerts"
    )
):
    """
    Get recent weather alerts.
    
    Args:
        city: Filter by city (optional)
        hours: Number of hours to look back
        limit: Maximum number of alerts
        
    Returns:
        List of recent alerts
    """
    return await alert_controller.get_recent_alerts(city, hours, limit)


@router.post(
    "/{alert_id}/acknowledge",
    summary="Acknowledge Alert",
    description="Mark an alert as acknowledged"
)
async def acknowledge_alert(alert_id: str, request: AlertAcknowledgeRequest):
    """
    Mark an alert as acknowledged.
    
    Args:
        alert_id: Alert ID to acknowledge
        request: Acknowledgement details
        
    Returns:
        Success confirmation
    """
    return await alert_controller.acknowledge_alert(alert_id, request)


@router.get(
    "/statistics",
    summary="Get Alert Statistics",
    description="Get aggregated alert statistics for a time period"
)
async def get_alert_statistics(
    city: Optional[str] = None,
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Hours to analyze"
    )
):
    """
    Get alert statistics.
    
    Args:
        city: Filter by city (optional)
        hours: Number of hours to analyze
        
    Returns:
        Alert statistics
    """
    return await alert_controller.get_alert_statistics(city, hours)


@router.post(
    "/check",
    summary="Trigger Alert Check",
    description="Manually trigger weather alert checking"
)
async def trigger_alert_check(city: Optional[str] = "Pune"):
    """
    Manually trigger alert check.
    Useful for immediate checking or troubleshooting.
    
    Args:
        city: City name
        
    Returns:
        Status message with created alerts
    """
    return await alert_controller.trigger_alert_check(city)
