"""
Alert Controller
HTTP request handling for alert endpoints
"""

from typing import Dict, Any, List, Optional
from fastapi import Query, status

from ...common.base_controller import BaseController
from ...common.exceptions import NotFoundException
from ...models.alert import (
    AlertResponse,
    AlertAcknowledgeRequest,
    AlertStatsResponse,
    AlertCondition
)
from .alert_service import AlertService


class AlertController(BaseController):
    """Controller for alert-related HTTP endpoints"""
    
    def __init__(self):
        """Initialize alert controller with service"""
        super().__init__()
        self.service = AlertService()
    
    async def get_active_alerts(
        self,
        city: Optional[str] = None,
        limit: int = Query(
            default=50,
            ge=1,
            le=100,
            description="Maximum number of alerts"
        )
    ) -> Dict[str, Any]:
        """
        Get active (unacknowledged) weather alerts
        
        Args:
            city: Optional city filter
            limit: Maximum number of alerts
            
        Returns:
            Success response with active alerts
        """
        try:
            self.logger.info("Active alerts requested (city: %s)", city or "all")
            
            alerts_data = await self.service.get_active_alerts(city, limit)
            
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
                ).model_dump()
                for alert in alerts_data
            ]
            
            self.logger.info("Returning %s active alerts", len(alerts))
            
            return self.success_response(
                data=alerts,
                message=f"Active alerts for {city or 'all cities'}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_recent_alerts(
        self,
        city: Optional[str] = None,
        hours: int = Query(
            default=24,
            ge=1,
            le=168,
            description="Hours of history"
        ),
        limit: int = Query(
            default=100,
            ge=1,
            le=200,
            description="Maximum number of alerts"
        )
    ) -> Dict[str, Any]:
        """
        Get recent alerts within specified hours
        
        Args:
            city: Optional city filter
            hours: Number of hours to look back
            limit: Maximum number of alerts
            
        Returns:
            Success response with recent alerts
        """
        try:
            self.logger.info(
                "Recent alerts requested (city: %s, hours: %s)",
                city or "all",
                hours
            )
            
            alerts_data = await self.service.get_recent_alerts(city, hours, limit)
            
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
                    metadata=alert.get("metadata", {}),
                    acknowledged_at=alert.get("acknowledged_at"),
                    acknowledged_by=alert.get("acknowledged_by")
                ).model_dump()
                for alert in alerts_data
            ]
            
            self.logger.info("Returning %s recent alerts", len(alerts))
            
            return self.success_response(
                data=alerts,
                message=f"Recent alerts for {city or 'all cities'}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        request: AlertAcknowledgeRequest
    ) -> Dict[str, Any]:
        """
        Mark alert as acknowledged
        
        Args:
            alert_id: Alert ID
            request: Acknowledgement request with user info
            
        Returns:
            Success response
        """
        try:
            self.logger.info(
                "Acknowledging alert %s by %s",
                alert_id,
                request.acknowledged_by
            )
            
            success = await self.service.acknowledge_alert(
                alert_id,
                request.acknowledged_by
            )
            
            return self.success_response(
                data={"alert_id": alert_id, "acknowledged": success},
                message="Alert acknowledged successfully",
                status_code=status.HTTP_200_OK
            )
            
        except NotFoundException as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_alert_statistics(
        self,
        city: Optional[str] = None,
        hours: int = Query(
            default=24,
            ge=1,
            le=168,
            description="Hours to analyze"
        )
    ) -> Dict[str, Any]:
        """
        Get alert statistics
        
        Args:
            city: Optional city filter
            hours: Number of hours to analyze
            
        Returns:
            Success response with statistics
        """
        try:
            self.logger.info(
                "Alert statistics requested (city: %s, hours: %s)",
                city or "all",
                hours
            )
            
            stats = await self.service.get_alert_stats(city, hours)
            
            # Transform to response model
            response = AlertStatsResponse(
                period_hours=stats["period_hours"],
                city=stats["city"],
                alerts_by_type=stats["alerts_by_type"],
                total_alerts=sum(
                    type_stats["total"]
                    for type_stats in stats["alerts_by_type"].values()
                ),
                total_acknowledged=sum(
                    type_stats["acknowledged"]
                    for type_stats in stats["alerts_by_type"].values()
                ),
                total_active=sum(
                    type_stats["active"]
                    for type_stats in stats["alerts_by_type"].values()
                )
            )
            
            return self.success_response(
                data=response.model_dump(),
                message=f"Alert statistics for {city or 'all cities'}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    async def trigger_alert_check(
        self,
        city: Optional[str] = "Pune"
    ) -> Dict[str, Any]:
        """
        Manually trigger alert check
        
        Args:
            city: City name
            
        Returns:
            Success response with created alert IDs
        """
        try:
            self.logger.info("Alert check triggered for %s", city)
            
            alert_ids = await self.service.check_and_create_alerts(city)
            
            return self.success_response(
                data={
                    "city": city,
                    "alerts_created": len(alert_ids),
                    "alert_ids": alert_ids
                },
                message=f"Alert check completed for {city}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
