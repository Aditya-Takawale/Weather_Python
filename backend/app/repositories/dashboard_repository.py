"""
Dashboard Summary Repository
Database operations for dashboard summary data
"""

from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection

from ..config.database import DatabaseManager
from ..config.settings import settings
from ..models.dashboard import DashboardSummary
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DashboardRepository:
    """Repository for dashboardsummaries collection operations"""
    
    @classmethod
    def _get_collection(cls) -> AsyncIOMotorCollection:
        """Get dashboard summaries collection"""
        return DatabaseManager.get_collection(settings.COLLECTION_DASHBOARD_SUMMARY)
    
    @classmethod
    async def upsert_summary(cls, summary: DashboardSummary) -> str:
        """
        Insert or update dashboard summary
        Replaces existing summary for the same city and type
        
        Args:
            summary: Dashboard summary data
            
        Returns:
            Document ID
        """
        try:
            collection = cls._get_collection()
            document = summary.model_dump()
            
            # Upsert: replace existing or insert new
            result = await collection.replace_one(
                {"city": summary.city, "summary_type": summary.summary_type},
                document,
                upsert=True
            )
            
            if result.upserted_id:
                doc_id = str(result.upserted_id)
                logger.info(f"Inserted new dashboard summary for {summary.city}")
            else:
                doc_id = str(result.modified_count)
                logger.info(f"Updated dashboard summary for {summary.city}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Error upserting dashboard summary: {e}")
            raise
    
    @classmethod
    async def get_latest_summary(
        cls,
        city: str,
        summary_type: str = "hourly"
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest dashboard summary for a city
        
        Args:
            city: City name
            summary_type: Type of summary (default: hourly)
            
        Returns:
            Dashboard summary document or None
        """
        try:
            collection = cls._get_collection()
            
            document = await collection.find_one(
                {"city": city, "summary_type": summary_type},
                sort=[("generated_at", -1)]
            )
            
            if document:
                document["_id"] = str(document["_id"])
            
            return document
            
        except Exception as e:
            logger.error(f"Error fetching latest summary: {e}")
            raise
    
    @classmethod
    async def delete_old_summaries(cls, city: str, keep_latest: int = 1) -> int:
        """
        Delete old summary records, keeping only the latest N
        
        Args:
            city: City name
            keep_latest: Number of latest summaries to keep
            
        Returns:
            Number of deleted documents
        """
        try:
            collection = cls._get_collection()
            
            # Find IDs of summaries to delete
            pipeline = [
                {"$match": {"city": city}},
                {"$sort": {"generated_at": -1}},
                {"$skip": keep_latest},
                {"$project": {"_id": 1}}
            ]
            
            cursor = collection.aggregate(pipeline)
            to_delete = await cursor.to_list(length=None)
            
            if not to_delete:
                return 0
            
            ids_to_delete = [doc["_id"] for doc in to_delete]
            
            result = await collection.delete_many(
                {"_id": {"$in": ids_to_delete}}
            )
            
            count = result.deleted_count
            logger.info(f"Deleted {count} old dashboard summaries for {city}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error deleting old summaries: {e}")
            raise
    
    @classmethod
    async def get_summary_count(cls, city: str) -> int:
        """
        Get count of summaries for a city
        
        Args:
            city: City name
            
        Returns:
            Number of summaries
        """
        try:
            collection = cls._get_collection()
            count = await collection.count_documents({"city": city})
            return count
            
        except Exception as e:
            logger.error(f"Error counting summaries: {e}")
            raise
