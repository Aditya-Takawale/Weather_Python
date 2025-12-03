"""
Alerts API Routes
Endpoints for weather alert management
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from ...models.alert import (
    AlertResponse,
    AlertAcknowledgeRequest,
    AlertStatsResponse,
    AlertCondition
)
from ...utils.logger import get_logger
# Legacy file - Use ../alerts/alert_router.py instead
# Kept for backward compatibility only

logger = get_logger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get(
    "/active",
    response_model=List[AlertResponse],
    summary="Get Active Alerts",
    description="Get all unacknowledged weather alerts"
)
async def get_active_alerts(
    city: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of alerts to return")
):
    """
    Get active (unacknowledged) weather alerts.

    Args:
        city: Filter by city (optional)
        limit: Maximum number of alerts

    Returns:
        List of active alerts
    """
    try:
        logger.info(f"Active alerts requested (city: {city or 'all'})")

        alerts_data = await AlertService.get_active_alerts(city, limit)

        # Transform to response models
        alerts = [
            AlertResponse(
                id=alert["_id"],
                city=alert["city"],
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                message=alert["message"],
                triggered_at=alert["triggered_at"],
                is_acknowledged=alert["is_acknowledged"],
                condition=AlertCondition(**alert["condition"]),
                metadata=alert.get("metadata", {})
            )
            for alert in alerts_data
        ]

        logger.info(f"Returning {len(alerts)} active alerts")
        return alerts

    except Exception as e:
        logger.error(f"Error fetching active alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active alerts"
        ) from e


@router.get(
    "/recent",
    response_model=List[AlertResponse],
    summary="Get Recent Alerts",
    description="Get recent alerts for a city within specified time range"
)
async def get_recent_alerts(
    city: str = Query(..., description="City name"),
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back")
):
    """
    Get recent alerts for a city.

    Args:
        city: City name
        hours: Number of hours to look back

    Returns:
        List of recent alerts
    """
    try:
        logger.info(f"Recent alerts requested for {city} (last {hours} hours)")

        alerts_data = await AlertService.get_recent_alerts(city, hours)

        # Transform to response models
        alerts = [
            AlertResponse(
                id=alert["_id"],
                city=alert["city"],
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                message=alert["message"],
                triggered_at=alert["triggered_at"],
                is_acknowledged=alert["is_acknowledged"],
                condition=AlertCondition(**alert["condition"]),
                metadata=alert.get("metadata", {})
            )
            for alert in alerts_data
        ]

        return alerts

    except Exception as e:
        logger.error(f"Error fetching recent alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent alerts"
        ) from e


@router.post(
    "/acknowledge",
    summary="Acknowledge Alert",
    description="Mark an alert as acknowledged"
)
async def acknowledge_alert(request: AlertAcknowledgeRequest):
    """
    Acknowledge a weather alert.

    Args:
        request: Alert acknowledgment request

    Returns:
        Acknowledgment status
    """
    try:
        logger.info(f"Acknowledging alert: {request.alert_id}")

        success = await AlertService.acknowledge_alert(request.alert_id)

        if success:
            return {
                "success": True,
                "message": "Alert acknowledged successfully",
                "alert_id": request.alert_id,
                "acknowledged_at": datetime.utcnow()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or already acknowledged"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        ) from e


@router.get(
    "/statistics",
    response_model=AlertStatsResponse,
    summary="Get Alert Statistics",
    description="Get aggregated alert statistics"
)
async def get_alert_statistics(city: Optional[str] = None):
    """
    Get alert statistics.

    Args:
        city: Filter by city (optional)

    Returns:
        Alert statistics
    """
    try:
        logger.info(f"Alert statistics requested (city: {city or 'all'})")

        stats = await AlertService.get_alert_stats(city)

        response = AlertStatsResponse(
            total_alerts=stats.get("total_alerts", 0),
            active_alerts=stats.get("active_alerts", 0),
            by_severity=stats.get("by_severity", {}),
            by_type=stats.get("by_type", {}),
            recent_alerts=stats.get("recent_alerts", 0)
        )

        return response

    except Exception as e:
        logger.error(f"Error fetching alert statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert statistics"
        ) from e


@router.post(
    "/check",
    summary="Trigger Alert Check",
    description="Manually trigger alert condition checking"
)
async def trigger_alert_check(city: Optional[str] = "Pune"):
    """
    Manually trigger alert checking for a city.

    Args:
        city: City name

    Returns:
        Alert check result
    """
    try:
        logger.info(f"Manual alert check triggered for {city}")

        alert_ids = await AlertService.check_and_create_alerts(city)

        return {
            "success": True,
            "message": f"Alert check completed for {city}",
            "alerts_triggered": len(alert_ids),
            "alert_ids": alert_ids,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Error triggering alert check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger alert check"
        ) from e
