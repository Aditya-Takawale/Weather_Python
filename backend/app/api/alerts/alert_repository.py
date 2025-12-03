"""
Alert Repository
Database operations for alert logs using OOP pattern
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from ...common.base_repository import BaseRepository
from ...models.alert import AlertLog, AlertType
from ...infrastructure.config import settings


class AlertRepository(BaseRepository[AlertLog]):
    """Repository for alertlogs collection operations"""
    
    def __init__(self):
        """Initialize alert repository"""
        super().__init__(settings.COLLECTION_ALERT_LOGS)
    
    async def insert_alert(self, alert: AlertLog) -> str:
        """
        Insert alert log into database
        
        Args:
            alert: Alert data to insert
            
        Returns:
            Inserted document ID
        """
        try:
            document = alert.model_dump()
            result_id = await self.insert_one(document)
            
            self.logger.info("Inserted alert: %s for %s", alert.alert_type, alert.city)
            
            return result_id
            
        except Exception as e:
            self.logger.error("Error inserting alert: %s", e)
            raise
    
    async def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get alert by ID
        
        Args:
            alert_id: Alert document ID
            
        Returns:
            Alert document or None
        """
        try:
            return await self.find_by_id(alert_id)
            
        except Exception as e:
            self.logger.error("Error fetching alert by ID: %s", e)
            raise
    
    async def get_active_alerts(
        self,
        city: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get active (unacknowledged) alerts
        
        Args:
            city: Optional city filter
            limit: Maximum number of alerts to return
            
        Returns:
            List of active alert documents
        """
        try:
            filter_dict: Dict[str, Any] = {"is_acknowledged": False}
            
            if city:
                filter_dict["city"] = city
            
            alerts = await self.find_many(
                filter_dict=filter_dict,
                sort=[("triggered_at", -1)],
                limit=limit
            )
            
            return alerts
            
        except Exception as e:
            self.logger.error("Error fetching active alerts: %s", e)
            raise
    
    async def get_recent_alerts(
        self,
        city: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts within specified hours
        
        Args:
            city: Optional city filter
            hours: Number of hours to look back
            limit: Maximum number of alerts
            
        Returns:
            List of recent alert documents
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            filter_dict: Dict[str, Any] = {
                "triggered_at": {"$gte": cutoff_time}
            }
            
            if city:
                filter_dict["city"] = city
            
            alerts = await self.find_many(
                filter_dict=filter_dict,
                sort=[("triggered_at", -1)],
                limit=limit
            )
            
            return alerts
            
        except Exception as e:
            self.logger.error("Error fetching recent alerts: %s", e)
            raise
    
    async def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """
        Mark alert as acknowledged
        
        Args:
            alert_id: Alert document ID
            user: User who acknowledged
            
        Returns:
            True if successful
        """
        try:
            success = await self.update_one(
                filter_dict={"_id": ObjectId(alert_id)},
                update_dict={
                    "$set": {
                        "is_acknowledged": True,
                        "acknowledged_by": user,
                        "acknowledged_at": datetime.utcnow()
                    }
                }
            )
            
            if success:
                self.logger.info("Alert %s acknowledged by %s", alert_id, user)
            
            return success
            
        except Exception as e:
            self.logger.error("Error acknowledging alert: %s", e)
            raise
    
    async def get_alert_stats(
        self,
        city: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get alert statistics for a time period
        
        Args:
            city: Optional city filter
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with alert statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            match_stage: Dict[str, Any] = {
                "triggered_at": {"$gte": cutoff_time}
            }
            
            if city:
                match_stage["city"] = city
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": "$alert_type",
                        "count": {"$sum": 1},
                        "acknowledged": {
                            "$sum": {"$cond": ["$is_acknowledged", 1, 0]}
                        }
                    }
                }
            ]
            
            results = await self.aggregate(pipeline)
            
            stats = {
                "period_hours": hours,
                "city": city or "all",
                "alerts_by_type": {
                    result["_id"]: {
                        "total": result["count"],
                        "acknowledged": result["acknowledged"],
                        "active": result["count"] - result["acknowledged"]
                    }
                    for result in results
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error("Error getting alert stats: %s", e)
            raise
