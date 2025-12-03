"""
Base Repository Class
Generic database operations with OOP principles
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from ..infrastructure.database import DatabaseManager
from ..core.logging import get_logger

T = TypeVar('T')
logger = get_logger(__name__)


class BaseRepository(Generic[T]):
    """
    Generic repository base class for MongoDB operations
    Follows repository pattern with dependency injection
    """
    
    def __init__(self, collection_name: str):
        """
        Initialize repository with collection name
        
        Args:
            collection_name: MongoDB collection name
        """
        self.collection_name = collection_name
        self._collection: Optional[AsyncIOMotorCollection] = None
        self.logger = get_logger(self.__class__.__name__)
    
    @property
    def collection(self) -> AsyncIOMotorCollection:  # type: ignore
        """Lazy load collection"""
        if self._collection is None:
            self._collection = DatabaseManager.get_collection(self.collection_name)
        return self._collection
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Find document by ID
        
        Args:
            id: Document ObjectId as string
            
        Returns:
            Document dictionary or None
        """
        try:
            result = await self.collection.find_one({"_id": ObjectId(id)})
            return result
        except Exception as e:
            self.logger.error("Error finding document by id %s: %s", id, e)
            return None
    
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find single document by filter
        
        Args:
            filter_dict: MongoDB filter query
            
        Returns:
            Document dictionary or None
        """
        try:
            result = await self.collection.find_one(filter_dict)
            return result
        except Exception as e:
            self.logger.error("Error finding document: %s", e)
            return None
    
    async def find_many(
        self,
        filter_dict: Dict[str, Any],
        limit: Optional[int] = None,
        skip: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents
        
        Args:
            filter_dict: MongoDB filter query
            limit: Maximum documents to return
            skip: Number of documents to skip
            sort: Sort specification
            
        Returns:
            List of document dictionaries
        """
        try:
            cursor = self.collection.find(filter_dict)
            
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            if sort:
                cursor = cursor.sort(sort)
            
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            self.logger.error("Error finding documents: %s", e)
            return []
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert single document
        
        Args:
            document: Document to insert
            
        Returns:
            Inserted document ID
        """
        try:
            result = await self.collection.insert_one(document)
            self.logger.info("Inserted document with id: %s", result.inserted_id)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error("Error inserting document: %s", e)
            raise
    
    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents
        
        Args:
            documents: List of documents to insert
            
        Returns:
            List of inserted document IDs
        """
        try:
            result = await self.collection.insert_many(documents)
            ids = [str(id) for id in result.inserted_ids]
            self.logger.info("Inserted %d documents", len(ids))
            return ids
        except Exception as e:
            self.logger.error("Error inserting documents: %s", e)
            raise
    
    async def update_one(
        self,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any]
    ) -> bool:
        """
        Update single document
        
        Args:
            filter_dict: MongoDB filter query
            update_dict: Update operations
            
        Returns:
            True if updated, False otherwise
        """
        try:
            result = await self.collection.update_one(filter_dict, update_dict)
            return result.modified_count > 0
        except Exception as e:
            self.logger.error("Error updating document: %s", e)
            return False
    
    async def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """
        Delete single document
        
        Args:
            filter_dict: MongoDB filter query
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one(filter_dict)
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error("Error deleting document: %s", e)
            return False
    
    async def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """
        Delete multiple documents
        
        Args:
            filter_dict: MongoDB filter query
            
        Returns:
            Number of deleted documents
        """
        try:
            result = await self.collection.delete_many(filter_dict)
            return result.deleted_count
        except Exception as e:
            self.logger.error("Error deleting documents: %s", e)
            return 0
    
    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents
        
        Args:
            filter_dict: MongoDB filter query (optional)
            
        Returns:
            Document count
        """
        try:
            count = await self.collection.count_documents(filter_dict or {})
            return count
        except Exception as e:
            self.logger.error("Error counting documents: %s", e)
            return 0
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run aggregation pipeline
        
        Args:
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            List of aggregation results
        """
        try:
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            self.logger.error("Error running aggregation: %s", e)
            return []
