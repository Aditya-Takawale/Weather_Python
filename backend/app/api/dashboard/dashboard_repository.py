"""
Dashboard Summary Repository
Database operations for dashboard summary data using OOP pattern
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from ...common.base_repository import BaseRepository
from ...models.dashboard import DashboardSummary
from ...infrastructure.config import settings


class DashboardRepository(BaseRepository[DashboardSummary]):
    """Repository for dashboardsummaries collection operations"""
    
    def __init__(self):
        """Initialize dashboard repository"""
        super().__init__(settings.COLLECTION_DASHBOARD_SUMMARY)
    
    async def upsert_summary(self, summary: DashboardSummary) -> str:
        """
        Insert or update dashboard summary
        Replaces existing summary for the same city and type
        
        Args:
            summary: Dashboard summary data
            
        Returns:
            Document ID
        """
        try:
            document = summary.model_dump()
            
            # Use raw collection for replace_one (not in base repository)
            collection = self._collection
            result = await collection.replace_one(
                {"city": summary.city, "summary_type": summary.summary_type},
                document,
                upsert=True
            )
            
            if result.upserted_id:
                doc_id = str(result.upserted_id)
                self.logger.info("Inserted new dashboard summary for %s", summary.city)
            else:
                doc_id = str(result.modified_count)
                self.logger.info("Updated dashboard summary for %s", summary.city)
            
            return doc_id
            
        except Exception as e:
            self.logger.error("Error upserting dashboard summary: %s", e)
            raise
    
    async def get_latest_summary(
        self,
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
            document = await self.find_one(
                filter_dict={"city": city, "summary_type": summary_type},
                sort=[("generated_at", -1)]
            )
            
            return document
            
        except Exception as e:
            self.logger.error("Error fetching latest summary: %s", e)
            raise
    
    async def delete_old_summaries(self, city: str, keep_latest: int = 1) -> int:
        """
        Delete old summary records, keeping only the latest N
        
        Args:
            city: City name
            keep_latest: Number of latest summaries to keep
            
        Returns:
            Number of deleted documents
        """
        try:
            # Get all summaries sorted by generated_at (newest first)
            summaries = await self.find_many(
                filter_dict={"city": city},
                sort=[("generated_at", -1)]
            )
            
            if len(summaries) <= keep_latest:
                self.logger.info("No old summaries to delete for %s", city)
                return 0
            
            # Get IDs of summaries to delete (skip the latest N)
            ids_to_delete = [
                summary["_id"]
                for summary in summaries[keep_latest:]
            ]
            
            # Delete old summaries
            count = await self.delete_many(
                filter_dict={"_id": {"$in": ids_to_delete}}
            )
            
            self.logger.info(
                "Deleted %s old summaries for %s",
                count,
                city
            )
            
            return count
            
        except Exception as e:
            self.logger.error("Error deleting old summaries: %s", e)
            raise
    
    async def get_summary_history(
        self,
        city: str,
        limit: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get recent summary history for a city
        
        Args:
            city: City name
            limit: Maximum number of summaries to return
            
        Returns:
            List of dashboard summary documents
        """
        try:
            summaries = await self.find_many(
                filter_dict={"city": city},
                sort=[("generated_at", -1)],
                limit=limit
            )
            
            return summaries
            
        except Exception as e:
            self.logger.error("Error fetching summary history: %s", e)
            raise
