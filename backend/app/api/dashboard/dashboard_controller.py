"""
Dashboard Controller
HTTP request handling for dashboard endpoints
"""

from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import status

from ...common.base_controller import BaseController
from ...common.exceptions import NotFoundException
from ...models.dashboard import DashboardSummary, DashboardSummaryResponse
from .dashboard_service import DashboardService


class DashboardController(BaseController):
    """Controller for dashboard-related HTTP endpoints"""
    
    def __init__(self):
        """Initialize dashboard controller with service"""
        super().__init__()
        self.service = DashboardService()
    
    async def get_dashboard_summary(
        self,
        city: Optional[str] = "Pune"
    ) -> Dict[str, Any]:
        """
        Get comprehensive pre-aggregated dashboard summary data
        
        Args:
            city: City name
            
        Returns:
            Success response with dashboard summary
        """
        try:
            self.logger.info("Dashboard summary requested for %s", city)
            
            # Get latest pre-computed summary from database
            try:
                summary_data = await self.service.get_latest_dashboard_summary(city)
            except NotFoundException:
                # No summary exists, generate one on-the-fly
                self.logger.info("No dashboard summary found, generating on-demand for %s", city)
                summary_data_obj = await self.service.generate_dashboard_summary(city)
                
                if not summary_data_obj:
                    # No weather data available yet
                    return self.error_response(
                        message=f"No weather data available for {city} yet. Please wait for data collection.",
                        status_code=status.HTTP_404_NOT_FOUND,
                        details={"city": city, "reason": "No weather data collected"}
                    )
                
                # Save it for future requests
                await self.service.save_dashboard_summary(summary_data_obj)
                summary_data = summary_data_obj.model_dump()
            
            # Convert to Pydantic model
            summary = DashboardSummary(**summary_data)
            
            # Build response
            response = DashboardSummaryResponse(
                success=True,
                data=summary,
                timestamp=datetime.utcnow()
            )
            
            self.logger.info("Dashboard summary served for %s", city)
            
            return self.success_response(
                data=response.model_dump(),
                message=f"Dashboard summary for {city}",
                status_code=status.HTTP_200_OK
            )
            
        except NotFoundException as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    async def trigger_dashboard_refresh(
        self,
        city: Optional[str] = "Pune"
    ) -> Dict[str, Any]:
        """
        Manually trigger dashboard summary regeneration
        
        Args:
            city: City name
            
        Returns:
            Success response with status
        """
        try:
            self.logger.info("Dashboard refresh triggered for %s", city)
            
            # Generate new summary
            summary = await self.service.generate_dashboard_summary(city)
            
            if not summary:
                return self.error_response(
                    message=f"Failed to generate dashboard summary for {city}",
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    details={"city": city}
                )
            
            # Save the generated summary
            saved = await self.service.save_dashboard_summary(summary)
            
            if not saved:
                return self.error_response(
                    message="Failed to save dashboard summary",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"city": city}
                )
            
            return self.success_response(
                data={
                    "city": city,
                    "generated_at": summary.generated_at.isoformat(),
                    "summary_type": summary.summary_type
                },
                message=f"Successfully refreshed dashboard for {city}",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)
