"""
Base service class with standardized interface patterns
Provides common functionality for all Rhiz Protocol services
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from datetime import datetime
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ValidationError

from app.core.exceptions import RhizProtocolError, ValidationError as RhizValidationError
from app.services.cache_service import cache_service

# Type variables for generic service operations
T = TypeVar('T')
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)


class BaseService(ABC, Generic[T]):
    """
    Abstract base class for all Rhiz Protocol services
    
    Provides standardized patterns for:
    - Database session management
    - Error handling and logging
    - Caching integration
    - Input validation
    - Metrics collection
    """
    
    def __init__(self, db: AsyncSession, logger: Optional[logging.Logger] = None):
        self.db = db
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._metrics: Dict[str, Any] = {}
        
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Service identifier for logging and metrics"""
        pass
    
    # Common CRUD patterns
    
    async def create(
        self, 
        create_data: CreateSchema, 
        validate: bool = True,
        cache_result: bool = True
    ) -> T:
        """
        Standard create operation with validation and caching
        
        Args:
            create_data: Validated input schema
            validate: Whether to perform additional validation
            cache_result: Whether to cache the created entity
        
        Returns:
            Created entity
            
        Raises:
            RhizValidationError: If validation fails
            RhizProtocolError: If creation fails
        """
        try:
            self.logger.info(f"Creating {self.service_name} entity")
            
            if validate:
                await self._validate_create_data(create_data)
            
            # Record start time for metrics
            start_time = datetime.utcnow()
            
            # Perform creation
            entity = await self._perform_create(create_data)
            
            # Record metrics
            self._record_operation_metric("create", start_time)
            
            # Cache if requested
            if cache_result and entity:
                await self._cache_entity(entity)
            
            self.logger.info(f"Successfully created {self.service_name} entity")
            return entity
            
        except ValidationError as e:
            self.logger.error(f"Validation error in {self.service_name}.create: {e}")
            raise RhizValidationError(f"Invalid {self.service_name} data: {e}")
        except Exception as e:
            self.logger.error(f"Error creating {self.service_name}: {e}")
            raise RhizProtocolError(f"Failed to create {self.service_name}: {e}")
    
    async def get_by_id(
        self, 
        entity_id: str, 
        use_cache: bool = True
    ) -> Optional[T]:
        """
        Standard get by ID with caching
        
        Args:
            entity_id: Unique identifier
            use_cache: Whether to check cache first
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            # Check cache first
            if use_cache:
                cached_entity = await self._get_from_cache(entity_id)
                if cached_entity:
                    self.logger.debug(f"Cache hit for {self.service_name}:{entity_id}")
                    return cached_entity
            
            # Record start time
            start_time = datetime.utcnow()
            
            # Fetch from database
            entity = await self._perform_get_by_id(entity_id)
            
            # Record metrics
            self._record_operation_metric("get_by_id", start_time)
            
            # Cache the result
            if entity and use_cache:
                await self._cache_entity(entity)
                
            return entity
            
        except Exception as e:
            self.logger.error(f"Error getting {self.service_name} by ID {entity_id}: {e}")
            raise RhizProtocolError(f"Failed to get {self.service_name}: {e}")
    
    async def update(
        self,
        entity_id: str,
        update_data: UpdateSchema,
        validate: bool = True
    ) -> Optional[T]:
        """
        Standard update operation with validation and cache invalidation
        
        Args:
            entity_id: Unique identifier
            update_data: Validated update schema
            validate: Whether to perform validation
            
        Returns:
            Updated entity if found, None otherwise
        """
        try:
            self.logger.info(f"Updating {self.service_name} entity {entity_id}")
            
            if validate:
                await self._validate_update_data(entity_id, update_data)
            
            start_time = datetime.utcnow()
            
            # Perform update
            entity = await self._perform_update(entity_id, update_data)
            
            # Record metrics
            self._record_operation_metric("update", start_time)
            
            # Invalidate cache
            await self._invalidate_cache(entity_id)
            
            # Cache updated entity
            if entity:
                await self._cache_entity(entity)
            
            self.logger.info(f"Successfully updated {self.service_name} entity {entity_id}")
            return entity
            
        except Exception as e:
            self.logger.error(f"Error updating {self.service_name} {entity_id}: {e}")
            raise RhizProtocolError(f"Failed to update {self.service_name}: {e}")
    
    async def delete(self, entity_id: str) -> bool:
        """
        Standard delete operation with cache invalidation
        
        Args:
            entity_id: Unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.logger.info(f"Deleting {self.service_name} entity {entity_id}")
            
            start_time = datetime.utcnow()
            
            # Perform deletion
            success = await self._perform_delete(entity_id)
            
            # Record metrics
            self._record_operation_metric("delete", start_time)
            
            # Invalidate cache
            if success:
                await self._invalidate_cache(entity_id)
            
            self.logger.info(f"Successfully deleted {self.service_name} entity {entity_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting {self.service_name} {entity_id}: {e}")
            raise RhizProtocolError(f"Failed to delete {self.service_name}: {e}")
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    async def _perform_create(self, create_data: CreateSchema) -> T:
        """Implement the actual creation logic"""
        pass
    
    @abstractmethod
    async def _perform_get_by_id(self, entity_id: str) -> Optional[T]:
        """Implement the actual get by ID logic"""
        pass
    
    @abstractmethod
    async def _perform_update(self, entity_id: str, update_data: UpdateSchema) -> Optional[T]:
        """Implement the actual update logic"""
        pass
    
    @abstractmethod
    async def _perform_delete(self, entity_id: str) -> bool:
        """Implement the actual deletion logic"""
        pass
    
    # Validation hooks (can be overridden)
    
    async def _validate_create_data(self, create_data: CreateSchema) -> None:
        """Override to add custom create validation"""
        pass
    
    async def _validate_update_data(self, entity_id: str, update_data: UpdateSchema) -> None:
        """Override to add custom update validation"""
        pass
    
    # Caching integration
    
    async def _cache_entity(self, entity: T) -> None:
        """Cache an entity (override for custom caching logic)"""
        if hasattr(entity, 'id'):
            await cache_service.cache_entity(
                entity_id=str(entity.id),
                entity_data=self._entity_to_dict(entity)
            )
    
    async def _get_from_cache(self, entity_id: str) -> Optional[T]:
        """Get entity from cache (override for custom cache retrieval)"""
        cached_data = await cache_service.get_entity(entity_id)
        if cached_data:
            return self._dict_to_entity(cached_data)
        return None
    
    async def _invalidate_cache(self, entity_id: str) -> None:
        """Invalidate cached entity"""
        await cache_service.invalidate_entity(entity_id)
    
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary for caching (override if needed)"""
        if hasattr(entity, '__dict__'):
            return {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
        return {}
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to entity (must be overridden)"""
        raise NotImplementedError("Subclasses must implement _dict_to_entity")
    
    # Metrics and monitoring
    
    def _record_operation_metric(self, operation: str, start_time: datetime) -> None:
        """Record operation timing metrics"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        if operation not in self._metrics:
            self._metrics[operation] = {
                'count': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0
            }
        
        self._metrics[operation]['count'] += 1
        self._metrics[operation]['total_duration'] += duration
        self._metrics[operation]['avg_duration'] = (
            self._metrics[operation]['total_duration'] / 
            self._metrics[operation]['count']
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return {
            'service_name': self.service_name,
            'operations': self._metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # Context managers for database transactions
    
    @asynccontextmanager
    async def transaction(self):
        """Database transaction context manager"""
        try:
            await self.db.begin()
            yield self.db
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Transaction failed for {self.service_name}: {e}")
            raise
    
    # Batch operations
    
    async def batch_create(
        self, 
        create_data_list: List[CreateSchema],
        batch_size: int = 100
    ) -> List[T]:
        """
        Batch create operation for improved performance
        
        Args:
            create_data_list: List of create schemas
            batch_size: Number of items to process per batch
            
        Returns:
            List of created entities
        """
        created_entities = []
        
        for i in range(0, len(create_data_list), batch_size):
            batch = create_data_list[i:i + batch_size]
            
            async with self.transaction():
                batch_results = await asyncio.gather(
                    *[self._perform_create(item) for item in batch],
                    return_exceptions=True
                )
                
                # Filter out exceptions and log them
                for result in batch_results:
                    if isinstance(result, Exception):
                        self.logger.error(f"Batch create error: {result}")
                    else:
                        created_entities.append(result)
        
        self.logger.info(f"Batch created {len(created_entities)} {self.service_name} entities")
        return created_entities
    
    # Health check
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            # Test database connection
            result = await self.db.execute("SELECT 1")
            db_healthy = result.scalar() == 1
            
            return {
                'service': self.service_name,
                'healthy': db_healthy,
                'database': 'connected' if db_healthy else 'disconnected',
                'metrics': self.get_metrics(),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed for {self.service_name}: {e}")
            return {
                'service': self.service_name,
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }