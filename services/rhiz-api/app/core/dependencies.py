"""
Dependency injection system for Rhiz Protocol
Provides clean separation of concerns and testability
"""

from typing import AsyncGenerator, Optional
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import RhizProtocolSettings, get_settings
from app.database import get_db
from app.services.trust_engine import TrustEngine
from app.services.pathfinder import PathFinder
from app.services.semantic_search import SemanticSearchService
from app.services.signature_verification import SignatureVerificationService
from app.services.cache_service import CacheService, cache_service


# Configuration dependency
async def get_config() -> RhizProtocolSettings:
    """Get application configuration"""
    return get_settings()


# Database dependencies
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with get_db() as session:
        yield session


# Cache service dependency
@lru_cache()
def get_cache_service() -> CacheService:
    """Get cache service (singleton)"""
    return cache_service


# Service dependencies
async def get_trust_engine(
    db: AsyncSession = Depends(get_database_session),
    config: RhizProtocolSettings = Depends(get_config)
) -> TrustEngine:
    """Get trust engine service"""
    return TrustEngine(
        db=db,
        enable_privacy=config.trust_engine.enable_privacy
    )


async def get_pathfinder(
    db: AsyncSession = Depends(get_database_session)
) -> PathFinder:
    """Get pathfinder service"""
    return PathFinder(db=db)


async def get_semantic_search(
    db: AsyncSession = Depends(get_database_session)
) -> SemanticSearchService:
    """Get semantic search service"""
    return SemanticSearchService(db=db)


@lru_cache()
def get_signature_verification() -> SignatureVerificationService:
    """Get signature verification service (singleton)"""
    return SignatureVerificationService()


# Service factory for testing
class ServiceFactory:
    """Factory for creating service instances with custom dependencies"""
    
    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        config: Optional[RhizProtocolSettings] = None,
        cache_service: Optional[CacheService] = None
    ):
        self._db_session = db_session
        self._config = config or get_settings()
        self._cache_service = cache_service
    
    def create_trust_engine(self, db: Optional[AsyncSession] = None) -> TrustEngine:
        """Create trust engine instance"""
        session = db or self._db_session
        if not session:
            raise ValueError("Database session required")
        
        return TrustEngine(
            db=session,
            enable_privacy=self._config.trust_engine.enable_privacy
        )
    
    def create_pathfinder(self, db: Optional[AsyncSession] = None) -> PathFinder:
        """Create pathfinder instance"""
        session = db or self._db_session
        if not session:
            raise ValueError("Database session required")
        
        return PathFinder(db=session)
    
    def create_semantic_search(self, db: Optional[AsyncSession] = None) -> SemanticSearchService:
        """Create semantic search instance"""
        session = db or self._db_session
        if not session:
            raise ValueError("Database session required")
        
        return SemanticSearchService(db=session)
    
    def create_signature_verification(self) -> SignatureVerificationService:
        """Create signature verification instance"""
        return SignatureVerificationService()


# Health check dependencies
async def check_database_health(
    db: AsyncSession = Depends(get_database_session)
) -> dict:
    """Check database health"""
    try:
        result = await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "connected": result.scalar() == 1
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
        }


async def check_cache_health(
    cache: CacheService = Depends(get_cache_service)
) -> dict:
    """Check cache health"""
    try:
        await cache.connect()
        stats = await cache.get_cache_statistics()
        return {
            "status": "healthy",
            "connected": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
        }


# Authentication and authorization dependencies
async def verify_signature(
    signature_service: SignatureVerificationService = Depends(get_signature_verification)
) -> bool:
    """Verify request signature (placeholder)"""
    # In production, would extract and verify signature from request
    return True


async def require_authentication() -> str:
    """Require authenticated request (placeholder)"""
    # In production, would extract and validate DID from request
    return "did:plc:example"


# Utility dependencies
async def get_request_id() -> str:
    """Generate unique request ID for tracing"""
    import uuid
    return str(uuid.uuid4())


# Performance monitoring dependencies
class PerformanceMonitor:
    """Request performance monitoring"""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    async def start_request(self, request_id: str):
        """Start monitoring request"""
        from datetime import datetime
        self.start_time = datetime.utcnow()
        self.metrics[request_id] = {
            "start_time": self.start_time,
            "operations": []
        }
    
    async def record_operation(self, request_id: str, operation: str, duration: float):
        """Record operation timing"""
        if request_id in self.metrics:
            self.metrics[request_id]["operations"].append({
                "operation": operation,
                "duration": duration
            })
    
    async def finish_request(self, request_id: str) -> dict:
        """Finish monitoring and return metrics"""
        if request_id not in self.metrics:
            return {}
        
        from datetime import datetime
        end_time = datetime.utcnow()
        total_duration = (end_time - self.metrics[request_id]["start_time"]).total_seconds()
        
        metrics = self.metrics.pop(request_id)
        metrics["end_time"] = end_time
        metrics["total_duration"] = total_duration
        
        return metrics


@lru_cache()
def get_performance_monitor() -> PerformanceMonitor:
    """Get performance monitor (singleton)"""
    return PerformanceMonitor()


# Validation dependencies
async def validate_did(did: str) -> str:
    """Validate DID format"""
    from app.core.exceptions import invalid_did
    
    if not did.startswith(("did:plc:", "did:web:")):
        raise invalid_did(did, "DID must use plc or web method")
    
    if len(did) < 10:
        raise invalid_did(did, "DID too short")
    
    return did


async def validate_at_uri(uri: str) -> str:
    """Validate AT Protocol URI format"""
    from app.core.exceptions import ValidationError
    
    if not uri.startswith("at://"):
        raise ValidationError(
            message="Invalid AT URI format",
            field="uri",
            value=uri
        )
    
    return uri


# Context managers for service lifecycle
class ServiceContext:
    """Context manager for service lifecycle"""
    
    def __init__(self, factory: ServiceFactory):
        self.factory = factory
        self.services = {}
    
    async def __aenter__(self):
        # Initialize services
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup services
        for service in self.services.values():
            if hasattr(service, 'cleanup'):
                await service.cleanup()


# Batch operation dependencies
async def get_batch_processor():
    """Get batch processor for bulk operations"""
    class BatchProcessor:
        def __init__(self, batch_size: int = 100):
            self.batch_size = batch_size
        
        async def process_batch(self, items, processor_func):
            """Process items in batches"""
            results = []
            for i in range(0, len(items), self.batch_size):
                batch = items[i:i + self.batch_size]
                batch_results = await processor_func(batch)
                results.extend(batch_results)
            return results
    
    return BatchProcessor()


# Testing utilities
def create_test_dependencies():
    """Create dependencies for testing"""
    from unittest.mock import AsyncMock, MagicMock
    
    # Mock database session
    mock_db = AsyncMock()
    
    # Mock services
    mock_trust_engine = MagicMock()
    mock_pathfinder = MagicMock()
    mock_semantic_search = MagicMock()
    mock_signature_verification = MagicMock()
    mock_cache_service = MagicMock()
    
    return {
        "db": mock_db,
        "trust_engine": mock_trust_engine,
        "pathfinder": mock_pathfinder,
        "semantic_search": mock_semantic_search,
        "signature_verification": mock_signature_verification,
        "cache_service": mock_cache_service
    }