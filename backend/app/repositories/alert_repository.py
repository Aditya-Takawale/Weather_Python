"""
Alert Repository
Database operations for alert logs
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from ..config.database import DatabaseManager
from ..config.settings import settings
from ..models.alert import AlertLog, AlertType, AlertSeverity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AlertRepository:
    """Repository for alertlogs collection operations"""
    
    @classmethod
    def _get_collection(cls) -> AsyncIOMotorCollection:
        """Get alert logs collection"""
        return DatabaseManager.get_collection(settings.COLLECTION_ALERT_LOGS)
    
    @classmethod
    async def insert_alert(cls, alert: AlertLog) -> str:
        """
        Insert alert log into database
        
        Args:
            alert: Alert data to insert
            
        Returns:
            Inserted document ID
        """
        try:
            collection = cls._get_collection()
            document = alert.model_dump()
            
            result = await collection.insert_one(document)
            logger.info(f"Inserted alert: {alert.alert_type} for {alert.city}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error inserting alert: {e}")
            raise
    
    @classmethod
    async def get_alert_by_id(cls, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get alert by ID
        
        Args:
            alert_id: Alert document ID
            
        Returns:
            Alert document or None
        """
        try:
            collection = cls._get_collection()
            
            document = await collection.find_one({"_id": ObjectId(alert_id)})
            
            if document:
                document["_id"] = str(document["_id"])
            
            return document
            
        except Exception as e:
            logger.error(f"Error fetching alert by ID: {e}")
            raise
    
    @classmethod
    async def get_active_alerts(cls, city: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get active (unacknowledged) alerts
        
        Args:
            city: Filter by city (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of active alert documents
        """
        try:
            collection = cls._get_collection()
            
            query = {"is_acknowledged": False}
            if city:
                query["city"] = city
            
            cursor = collection.find(query).sort("triggered_at", -1).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
            
        except Exception as e:
            logger.error(f"Error fetching active alerts: {e}")
            raise
    
    @classmethod
    async def get_recent_alerts(
        cls,
        city: str,
        hours: int = 24,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts for a city
        
        Args:
            city: City name
            hours: Number of hours to look back
            limit: Maximum number of alerts
            
        Returns:
            List of alert documents
        """
        try:
            collection = cls._get_collection()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = {
                "city": city,
                "triggered_at": {"$gte": cutoff_time}
            }
            
            cursor = collection.find(query).sort("triggered_at", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=None)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
            
        except Exception as e:
            logger.error(f"Error fetching recent alerts: {e}")
            raise
    
    @classmethod
    async def check_recent_similar_alert(
        cls,
        city: str,
        alert_type: AlertType,
        minutes: int = 60
    ) -> bool:
        """
        Check if a similar alert was triggered recently (cooldown check)
        
        Args:
            city: City name
            alert_type: Type of alert
            minutes: Cooldown period in minutes
            
        Returns:
            True if similar alert exists within cooldown period
        """
        try:
            collection = cls._get_collection()
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            count = await collection.count_documents({
                "city": city,
                "alert_type": alert_type,
                "triggered_at": {"$gte": cutoff_time}
            })
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking recent similar alert: {e}")
            raise
    
    @classmethod
    async def acknowledge_alert(cls, alert_id: str) -> bool:
        """
        Mark an alert as acknowledged
        
        Args:
            alert_id: Alert document ID
            
        Returns:
            True if successfully acknowledged
        """
        try:
            collection = cls._get_collection()
            
            result = await collection.update_one(
                {"_id": ObjectId(alert_id)},
                {
                    "$set": {
                        "is_acknowledged": True,
                        "acknowledged_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            
            if success:
                logger.info(f"Acknowledged alert: {alert_id}")
            else:
                logger.warning(f"Alert not found or already acknowledged: {alert_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            raise
    
    @classmethod
    async def get_alert_stats(cls, city: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """
        Get alert statistics
        
        Args:
            city: Filter by city (optional)
            hours: Time range in hours
            
        Returns:
            Dictionary with alert statistics
        """
        try:
            collection = cls._get_collection()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            match_query: Dict[str, Any] = {}
            if city:
                match_query["city"] = city
            
            # Total alerts
            total_alerts = await collection.count_documents(match_query)
            
            # Active alerts
            active_query = {**match_query, "is_acknowledged": False}
            active_alerts = await collection.count_documents(active_query)
            
            # Recent alerts
            recent_query = {**match_query, "triggered_at": {"$gte": cutoff_time}}
            recent_alerts = await collection.count_documents(recent_query)
            
            # By severity
            severity_pipeline = [
                {"$match": match_query},
                {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
            ]
            severity_cursor = collection.aggregate(severity_pipeline)
            severity_results = await severity_cursor.to_list(length=None)
            by_severity = {item["_id"]: item["count"] for item in severity_results}
            
            # By type
            type_pipeline = [
                {"$match": match_query},
                {"$group": {"_id": "$alert_type", "count": {"$sum": 1}}}
            ]
            type_cursor = collection.aggregate(type_pipeline)
            type_results = await type_cursor.to_list(length=None)
            by_type = {item["_id"]: item["count"] for item in type_results}
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "recent_alerts": recent_alerts,
                "by_severity": by_severity,
                "by_type": by_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating alert stats: {e}")
            raise
    
    @classmethod
    async def delete_old_alerts(cls, days: int = 30) -> int:
        """
        Delete alert logs older than specified days
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of deleted alerts
        """
        try:
            collection = cls._get_collection()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await collection.delete_many(
                {"triggered_at": {"$lt": cutoff_date}}
            )
            
            count = result.deleted_count
            logger.info(f"Deleted {count} alert logs older than {days} days")
            
            return count
            
        except Exception as e:
            logger.error(f"Error deleting old alerts: {e}")
            raise
