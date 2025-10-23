# Protocol Improvements V3 - Implementation Blueprint

**Version**: 3.0 (Implementation Ready)
**Date**: October 23, 2025
**Status**: Final Plan → Begin Implementation

---

## 🎯 V3 Refinements

**V1**: High-level features from FundRhiz
**V2**: Analysis + integration points
**V3**: **Exact implementation blueprint with code structure**

### What's New in V3:

1. ✅ **Exact file structure and module organization**
2. ✅ **Complete class signatures with type hints**
3. ✅ **Integration sequence (what to build first)**
4. ✅ **Migration path from current code**
5. ✅ **Concrete test specifications**
6. ✅ **Database schema changes needed**

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Protocol API Layer                         │
│  /api/v1/* endpoints (existing + new health endpoints)       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                Infrastructure Services Layer                 │
├──────────────────┬──────────────────┬──────────────────────┤
│  Cache Service   │ Event Pipeline   │ Health Check Service │
│  (Redis/Memory)  │ (Async Workers)  │ (Monitoring)         │
└──────────────────┴──────────────────┴──────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│              Existing Business Logic Services                │
│  TrustEngine, PathFinder, ConvictionCalculator, etc.         │
└──────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Data Layer                                │
│         PostgreSQL          Redis          AT Protocol       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component 1: Unified Cache Service

### File Structure
```
services/rhiz-api/app/
├── infrastructure/
│   ├── __init__.py
│   └── cache/
│       ├── __init__.py
│       ├── base.py          # Abstract cache interface
│       ├── memory.py        # Memory backend implementation
│       ├── redis.py         # Redis backend implementation
│       └── service.py       # Main CacheService facade
└── services/
    └── cache_service.py     # Singleton instance + helper functions
```

### Exact Implementation

**`app/infrastructure/cache/base.py`**:
```python
from abc import ABC, abstractmethod
from typing import Any, Optional, List
from dataclasses import dataclass

@dataclass
class CacheStats:
    hits: int
    misses: int
    sets: int
    deletes: int
    hit_rate: float
    total_keys: int
    memory_usage_bytes: int

class CacheBackend(ABC):
    """Abstract cache backend interface"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL in seconds"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern (e.g., 'trust:*')"""
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connections"""
        pass
```

**`app/infrastructure/cache/memory.py`**:
```python
import time
from typing import Any, Optional, Dict, Tuple
from collections import defaultdict
import fnmatch
from .base import CacheBackend, CacheStats

class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend (for development/testing)"""

    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._max_size = max_size
        self._stats = defaultdict(int)

    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry is None or expiry > time.time():
                self._stats['hits'] += 1
                return value
            else:
                del self._cache[key]  # Expired
                self._stats['misses'] += 1
        else:
            self._stats['misses'] += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        # Evict oldest if at max size
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        expiry = time.time() + ttl if ttl else None
        self._cache[key] = (value, expiry)
        self._stats['sets'] += 1
        return True

    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            self._stats['deletes'] += 1
            return True
        return False

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching glob pattern"""
        matching_keys = [
            key for key in self._cache.keys()
            if fnmatch.fnmatch(key, pattern)
        ]
        for key in matching_keys:
            del self._cache[key]
        count = len(matching_keys)
        self._stats['deletes'] += count
        return count

    async def get_stats(self) -> CacheStats:
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0.0

        # Estimate memory usage (rough)
        import sys
        memory_bytes = sum(
            sys.getsizeof(k) + sys.getsizeof(v[0])
            for k, v in self._cache.items()
        )

        return CacheStats(
            hits=self._stats['hits'],
            misses=self._stats['misses'],
            sets=self._stats['sets'],
            deletes=self._stats['deletes'],
            hit_rate=hit_rate,
            total_keys=len(self._cache),
            memory_usage_bytes=memory_bytes
        )

    async def close(self) -> None:
        self._cache.clear()
```

**`app/infrastructure/cache/redis.py`**:
```python
import json
import pickle
from typing import Any, Optional
from redis.asyncio import Redis
from .base import CacheBackend, CacheStats

class RedisCacheBackend(CacheBackend):
    """Redis cache backend (for production)"""

    def __init__(self, redis_url: str):
        self._redis: Redis = Redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=False  # Handle binary data
        )
        self._stats_key = "cache:stats"

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self._redis.get(key)
            if value:
                # Increment hit counter
                await self._redis.hincrby(self._stats_key, "hits", 1)
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return pickle.loads(value)
            else:
                await self._redis.hincrby(self._stats_key, "misses", 1)
                return None
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            # Try JSON first, fallback to pickle
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)

            if ttl:
                await self._redis.setex(key, ttl, serialized)
            else:
                await self._redis.set(key, serialized)

            await self._redis.hincrby(self._stats_key, "sets", 1)
            return True
        except Exception as e:
            logging.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        count = await self._redis.delete(key)
        if count > 0:
            await self._redis.hincrby(self._stats_key, "deletes", 1)
        return count > 0

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern using SCAN"""
        deleted = 0
        async for key in self._redis.scan_iter(match=pattern):
            await self._redis.delete(key)
            deleted += 1

        if deleted > 0:
            await self._redis.hincrby(self._stats_key, "deletes", deleted)
        return deleted

    async def get_stats(self) -> CacheStats:
        stats_data = await self._redis.hgetall(self._stats_key)

        hits = int(stats_data.get(b'hits', 0))
        misses = int(stats_data.get(b'misses', 0))
        sets = int(stats_data.get(b'sets', 0))
        deletes = int(stats_data.get(b'deletes', 0))

        total_requests = hits + misses
        hit_rate = hits / total_requests if total_requests > 0 else 0.0

        # Get total keys and memory
        total_keys = await self._redis.dbsize()
        info = await self._redis.info('memory')
        memory_bytes = info.get('used_memory', 0)

        return CacheStats(
            hits=hits,
            misses=misses,
            sets=sets,
            deletes=deletes,
            hit_rate=hit_rate,
            total_keys=total_keys,
            memory_usage_bytes=memory_bytes
        )

    async def close(self) -> None:
        await self._redis.close()
```

**`app/infrastructure/cache/service.py`**:
```python
from typing import Any, Optional
from .base import CacheBackend, CacheStats
from .memory import MemoryCacheBackend
from .redis import RedisCacheBackend
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """
    Unified cache service with automatic fallback

    Usage:
        cache = CacheService(backend="redis", redis_url="redis://localhost:6379")
        await cache.set("trust:alice", {"score": 88}, ttl=3600)
        score = await cache.get("trust:alice")
    """

    def __init__(
        self,
        backend: str = "memory",
        redis_url: Optional[str] = None,
        fallback_to_memory: bool = True
    ):
        self._backend: CacheBackend
        self._fallback: Optional[CacheBackend] = None

        if backend == "redis":
            try:
                self._backend = RedisCacheBackend(redis_url or "redis://localhost:6379")
                if fallback_to_memory:
                    self._fallback = MemoryCacheBackend()
                logger.info("Cache service initialized with Redis (memory fallback)")
            except Exception as e:
                logger.warning(f"Redis init failed, using memory: {e}")
                self._backend = MemoryCacheBackend()
        else:
            self._backend = MemoryCacheBackend()
            logger.info("Cache service initialized with memory backend")

    async def get(self, key: str) -> Optional[Any]:
        try:
            return await self._backend.get(key)
        except Exception as e:
            logger.error(f"Cache backend error, trying fallback: {e}")
            if self._fallback:
                return await self._fallback.get(key)
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            success = await self._backend.set(key, value, ttl)
            if success and self._fallback:
                await self._fallback.set(key, value, ttl)  # Sync to fallback
            return success
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        success = await self._backend.delete(key)
        if self._fallback:
            await self._fallback.delete(key)
        return success

    async def clear_pattern(self, pattern: str) -> int:
        count = await self._backend.clear_pattern(pattern)
        if self._fallback:
            await self._fallback.clear_pattern(pattern)
        return count

    async def get_stats(self) -> CacheStats:
        return await self._backend.get_stats()

    async def health_check(self) -> dict:
        """Check cache health"""
        try:
            test_key = "health:check"
            await self._backend.set(test_key, "ok", ttl=1)
            value = await self._backend.get(test_key)
            await self._backend.delete(test_key)

            stats = await self.get_stats()

            return {
                "status": "healthy" if value == "ok" else "degraded",
                "backend": self._backend.__class__.__name__,
                "has_fallback": self._fallback is not None,
                "hit_rate": stats.hit_rate,
                "total_keys": stats.total_keys
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def close(self) -> None:
        await self._backend.close()
        if self._fallback:
            await self._fallback.close()
```

**`app/services/cache_service.py` (Singleton wrapper)**:
```python
"""
Global cache service instance
Provides easy access to unified cache throughout application
"""

from typing import Optional
from app.infrastructure.cache import CacheService
from app.config import settings

_cache_service: Optional[CacheService] = None

def get_cache_service() -> CacheService:
    """Get singleton cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(
            backend=settings.cache_backend,
            redis_url=settings.redis_url_string if settings.cache_backend == "redis" else None,
            fallback_to_memory=True
        )
    return _cache_service

async def close_cache_service():
    """Close cache service connections"""
    global _cache_service
    if _cache_service:
        await _cache_service.close()
        _cache_service = None
```

### Configuration Changes

**`app/config.py`** - Add:
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Cache Configuration
    cache_backend: str = Field(default="memory", alias="CACHE_BACKEND")  # "memory" or "redis"
    cache_default_ttl: int = Field(default=3600, alias="CACHE_DEFAULT_TTL")  # 1 hour
    cache_max_memory_size: int = Field(default=10000, alias="CACHE_MAX_MEMORY_SIZE")  # keys
```

### Integration Points

**Update `identity_resolver.py`**:
```python
# BEFORE: Local LRU cache
from functools import lru_cache
@lru_cache(maxsize=1000)
async def resolve_did_cached(self, did: str) -> ResolvedIdentity:
    return await self.resolve(did)

# AFTER: Unified cache service
from app.services.cache_service import get_cache_service

async def resolve_did_cached(self, did: str) -> ResolvedIdentity:
    cache = get_cache_service()
    cache_key = f"did:resolve:{did}"

    cached = await cache.get(cache_key)
    if cached:
        return ResolvedIdentity(**cached)

    resolved = await self.resolve(did)
    await cache.set(cache_key, resolved.__dict__, ttl=604800)  # 7 days
    return resolved
```

**Update `pathfinder.py`**:
```python
# BEFORE: Instance dict cache
self._graph_cache: Dict[str, Dict] = {}

# AFTER: Unified cache service
from app.services.cache_service import get_cache_service

async def find_path(...) -> GraphPathResponse | None:
    cache = get_cache_service()
    cache_key = f"graph:path:{from_entity}:{to_entity}:{max_hops}:{min_strength}"

    cached = await cache.get(cache_key)
    if cached and not force_refresh:
        return GraphPathResponse(**cached)

    path = await self._compute_path(...)
    await cache.set(cache_key, path.dict(), ttl=3600)  # 1 hour
    return path
```

**Update `trust_engine.py`**:
```python
async def calculate_trust_score(self, entity_id: str, ...) -> float:
    cache = get_cache_service()
    cache_key = f"trust:score:{entity_id}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    score = await self._compute_trust_score(entity_id, ...)
    await cache.set(cache_key, score, ttl=86400)  # 24 hours
    return score
```

### Database Schema (None needed - Redis external)

### Tests

**`app/tests/test_cache_service.py`**:
```python
import pytest
from app.infrastructure.cache import CacheService

@pytest.mark.asyncio
async def test_memory_backend():
    cache = CacheService(backend="memory")
    await cache.set("test", "value", ttl=60)
    assert await cache.get("test") == "value"
    await cache.close()

@pytest.mark.asyncio
async def test_redis_backend():
    cache = CacheService(backend="redis", redis_url="redis://localhost:6379")
    await cache.set("test", {"data": "value"}, ttl=60)
    result = await cache.get("test")
    assert result["data"] == "value"
    await cache.close()

@pytest.mark.asyncio
async def test_fallback_mechanism():
    # Simulate Redis failure
    cache = CacheService(backend="redis", redis_url="redis://invalid:9999")
    # Should fallback to memory
    await cache.set("test", "value")
    assert await cache.get("test") == "value"

@pytest.mark.asyncio
async def test_pattern_clearing():
    cache = CacheService(backend="memory")
    await cache.set("trust:alice", 88)
    await cache.set("trust:bob", 92)
    await cache.set("graph:path", "data")

    count = await cache.clear_pattern("trust:*")
    assert count == 2
    assert await cache.get("graph:path") == "data"
```

**Estimated**: 5-6 hours
**Priority**: 1 (Build first)

---

## 🔧 Component 2: Real-Time Event Pipeline

### File Structure
```
services/rhiz-api/app/
├── infrastructure/
│   └── events/
│       ├── __init__.py
│       ├── pipeline.py      # Main pipeline class
│       ├── types.py          # Event types and dataclasses
│       ├── processors/
│       │   ├── __init__.py
│       │   ├── base.py       # Abstract processor
│       │   ├── relationship.py
│       │   ├── attestation.py
│       │   └── entity.py
│       └── metrics.py        # Pipeline metrics
└── api/
    └── internal.py           # Internal endpoints for event ingestion
```

### Exact Implementation

**`app/infrastructure/events/types.py`**:
```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

class EventType(Enum):
    RELATIONSHIP_CREATED = "relationship.created"
    RELATIONSHIP_UPDATED = "relationship.updated"
    RELATIONSHIP_DELETED = "relationship.deleted"
    ATTESTATION_CREATED = "attestation.created"
    ENTITY_PROFILE_UPDATED = "entity.profile.updated"
    TRUST_SCORE_INVALIDATED = "trust.invalidated"

class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class ProtocolEvent:
    """Event in the protocol pipeline"""
    event_id: str
    event_type: EventType
    payload: Dict[str, Any]
    did: str  # DID that triggered the event
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    processing_stages: List[Dict[str, Any]] = field(default_factory=list)

    def add_stage_result(self, stage: str, success: bool, error: Optional[str] = None):
        self.processing_stages.append({
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "error": error
        })

@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""
    events_processed: int = 0
    events_failed: int = 0
    events_in_queue: int = 0
    avg_processing_time_ms: float = 0.0
    throughput_per_second: float = 0.0
    worker_utilization: float = 0.0
    backpressure_active: bool = False
```

**`app/infrastructure/events/processors/base.py`**:
```python
from abc import ABC, abstractmethod
from ..types import ProtocolEvent

class EventProcessor(ABC):
    """Abstract event processor"""

    @abstractmethod
    async def process(self, event: ProtocolEvent) -> bool:
        """Process event, return True if successful"""
        pass

    @abstractmethod
    def can_process(self, event: ProtocolEvent) -> bool:
        """Check if this processor can handle the event"""
        pass

    async def on_success(self, event: ProtocolEvent):
        """Called after successful processing"""
        pass

    async def on_failure(self, event: ProtocolEvent, error: Exception):
        """Called after failed processing"""
        pass
```

**`app/infrastructure/events/processors/relationship.py`**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.relationship import Relationship
from app.services.cache_service import get_cache_service
from .base import EventProcessor
from ..types import ProtocolEvent, EventType

class RelationshipEventProcessor(EventProcessor):
    """Process relationship events"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def can_process(self, event: ProtocolEvent) -> bool:
        return event.event_type in [
            EventType.RELATIONSHIP_CREATED,
            EventType.RELATIONSHIP_UPDATED,
            EventType.RELATIONSHIP_DELETED
        ]

    async def process(self, event: ProtocolEvent) -> bool:
        if event.event_type == EventType.RELATIONSHIP_CREATED:
            return await self._handle_created(event)
        elif event.event_type == EventType.RELATIONSHIP_UPDATED:
            return await self._handle_updated(event)
        elif event.event_type == EventType.RELATIONSHIP_DELETED:
            return await self._handle_deleted(event)
        return False

    async def _handle_created(self, event: ProtocolEvent) -> bool:
        # Index relationship in database
        # Invalidate graph caches for both participants
        cache = get_cache_service()
        participants = event.payload.get('participants', [])
        for did in participants:
            await cache.clear_pattern(f"graph:path:*{did}*")
        return True
```

**`app/infrastructure/events/pipeline.py`**:
```python
import asyncio
from typing import List, Dict, Optional
from collections import defaultdict
import time
import logging

from .types import ProtocolEvent, PipelineMetrics, EventPriority
from .processors.base import EventProcessor

logger = logging.getLogger(__name__)

class EventPipeline:
    """
    Real-time event processing pipeline

    Features:
    - Priority queues (critical events first)
    - Worker pool (configurable concurrency)
    - Backpressure (reject when queue full)
    - Retry logic (exponential backoff)
    - Dead letter queue (failed events)
    - Metrics tracking
    """

    def __init__(
        self,
        max_queue_size: int = 10000,
        num_workers: int = 10,
        backpressure_threshold: float = 0.8
    ):
        # Priority queues (one per priority level)
        self._queues: Dict[EventPriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=max_queue_size // 4)
            for priority in EventPriority
        }

        self._num_workers = num_workers
        self._backpressure_threshold = backpressure_threshold
        self._max_queue_size = max_queue_size

        # Event processors
        self._processors: List[EventProcessor] = []

        # Worker management
        self._workers: List[asyncio.Task] = []
        self._running = False

        # Dead letter queue
        self._dead_letter: List[ProtocolEvent] = []

        # Metrics
        self._metrics = PipelineMetrics()
        self._processing_times: List[float] = []

    def register_processor(self, processor: EventProcessor):
        """Register an event processor"""
        self._processors.append(processor)
        logger.info(f"Registered processor: {processor.__class__.__name__}")

    async def enqueue(self, event: ProtocolEvent) -> bool:
        """
        Enqueue event for processing

        Returns False if backpressure active (queue too full)
        """
        queue = self._queues[event.priority]

        # Check backpressure
        total_events = sum(q.qsize() for q in self._queues.values())
        if total_events >= self._max_queue_size * self._backpressure_threshold:
            logger.warning(f"Backpressure active: {total_events} events in queue")
            self._metrics.backpressure_active = True
            return False

        try:
            queue.put_nowait(event)
            self._metrics.events_in_queue += 1
            return True
        except asyncio.QueueFull:
            logger.error(f"Queue full for priority {event.priority}")
            return False

    async def start(self):
        """Start the pipeline and workers"""
        if self._running:
            raise RuntimeError("Pipeline already running")

        self._running = True
        logger.info(f"Starting event pipeline with {self._num_workers} workers")

        # Start workers
        for i in range(self._num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)

        # Start metrics calculator
        asyncio.create_task(self._calculate_metrics())

        logger.info("Event pipeline started")

    async def stop(self):
        """Stop the pipeline gracefully"""
        if not self._running:
            return

        logger.info("Stopping event pipeline...")
        self._running = False

        # Wait for workers to finish current events
        if self._workers:
            await asyncio.wait(self._workers, timeout=10.0)

        logger.info("Event pipeline stopped")

    async def _worker(self, name: str):
        """Worker that processes events from queues"""
        logger.info(f"Worker {name} started")

        while self._running:
            event = await self._get_next_event()
            if event is None:
                await asyncio.sleep(0.1)
                continue

            start_time = time.time()
            success = await self._process_event(event)
            processing_time = (time.time() - start_time) * 1000  # ms

            self._processing_times.append(processing_time)
            self._metrics.events_in_queue -= 1

            if success:
                self._metrics.events_processed += 1
            else:
                self._metrics.events_failed += 1
                if event.retry_count >= 3:
                    self._dead_letter.append(event)

        logger.info(f"Worker {name} stopped")

    async def _get_next_event(self) -> Optional[ProtocolEvent]:
        """Get next event from queues (priority order)"""
        for priority in sorted(EventPriority, key=lambda p: p.value, reverse=True):
            queue = self._queues[priority]
            if not queue.empty():
                return await queue.get()
        return None

    async def _process_event(self, event: ProtocolEvent) -> bool:
        """Process event through registered processors"""
        for processor in self._processors:
            if processor.can_process(event):
                try:
                    success = await processor.process(event)
                    if success:
                        await processor.on_success(event)
                        return True
                    else:
                        await processor.on_failure(event, Exception("Processing returned False"))
                except Exception as e:
                    logger.error(f"Processor failed: {e}")
                    await processor.on_failure(event, e)

                    # Retry logic
                    if event.retry_count < 3:
                        event.retry_count += 1
                        await asyncio.sleep(2 ** event.retry_count)  # Exponential backoff
                        await self.enqueue(event)

                    return False

        logger.warning(f"No processor for event type: {event.event_type}")
        return False

    async def _calculate_metrics(self):
        """Calculate pipeline metrics every second"""
        last_processed = 0

        while self._running:
            await asyncio.sleep(1.0)

            # Throughput
            current_processed = self._metrics.events_processed
            self._metrics.throughput_per_second = current_processed - last_processed
            last_processed = current_processed

            # Average processing time
            if self._processing_times:
                self._metrics.avg_processing_time_ms = sum(self._processing_times) / len(self._processing_times)
                self._processing_times.clear()

            # Worker utilization
            total_events = sum(q.qsize() for q in self._queues.values())
            self._metrics.events_in_queue = total_events
            self._metrics.worker_utilization = min(total_events / self._num_workers, 1.0)

    def get_metrics(self) -> PipelineMetrics:
        """Get current pipeline metrics"""
        return self._metrics

    def get_dead_letter_queue(self) -> List[ProtocolEvent]:
        """Get failed events for manual review"""
        return self._dead_letter.copy()
```

### API Endpoints

**`app/api/internal.py`** (NEW):
```python
"""
Internal API endpoints (not public-facing)
Used by TypeScript indexer to push events to Python pipeline
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Any, Dict
from app.infrastructure.events import get_event_pipeline
from app.infrastructure.events.types import ProtocolEvent, EventType, EventPriority
import uuid

router = APIRouter(prefix="/internal", tags=["internal"])

class IngestEventRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    did: str
    priority: int = 1

@router.post("/events")
async def ingest_event(
    request: IngestEventRequest,
    x_internal_key: str = Header(...)
):
    """
    Ingest event from TypeScript firehose indexer

    Requires X-Internal-Key header for authentication
    """
    # Validate internal key
    from app.config import settings
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=403, detail="Invalid internal key")

    # Create event
    event = ProtocolEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType(request.event_type),
        payload=request.payload,
        did=request.did,
        priority=EventPriority(request.priority)
    )

    # Enqueue
    pipeline = get_event_pipeline()
    success = await pipeline.enqueue(event)

    if not success:
        raise HTTPException(
            status_code=503,
            detail="Event pipeline backpressure active"
        )

    return {"status": "enqueued", "event_id": event.event_id}

@router.get("/events/metrics")
async def get_pipeline_metrics(x_internal_key: str = Header(...)):
    """Get event pipeline metrics"""
    from app.config import settings
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=403, detail="Invalid internal key")

    pipeline = get_event_pipeline()
    metrics = pipeline.get_metrics()

    return {
        "events_processed": metrics.events_processed,
        "events_failed": metrics.events_failed,
        "events_in_queue": metrics.events_in_queue,
        "avg_processing_time_ms": metrics.avg_processing_time_ms,
        "throughput_per_second": metrics.throughput_per_second,
        "worker_utilization": metrics.worker_utilization,
        "backpressure_active": metrics.backpressure_active
    }
```

**Estimated**: 8-10 hours
**Priority**: 2 (After cache service)

---

## 🔧 Component 3: Enhanced Health Checks

**File**: Enhance `app/api/health.py` (NEW, currently health in main.py)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.cache_service import get_cache_service
from app.infrastructure.events import get_event_pipeline
import time

router = APIRouter(prefix="/health", tags=["health"])

startup_time = time.time()

@router.get("")
async def liveness():
    """Fast liveness check"""
    return {"status": "healthy"}

@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """Readiness check with dependencies"""
    checks = {}

    # Database check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except:
        checks["database"] = "unhealthy"

    # Cache check
    cache = get_cache_service()
    cache_health = await cache.health_check()
    checks["cache"] = cache_health["status"]

    # Event pipeline check
    pipeline = get_event_pipeline()
    metrics = pipeline.get_metrics()
    checks["event_pipeline"] = "healthy" if metrics.events_in_queue < 8000 else "degraded"

    overall = "ready" if all(v == "healthy" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "checks": checks
    }

@router.get("/detailed")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """Detailed health with full diagnostics"""
    # All checks from readiness + more details
    # Database pool stats, Redis memory, Event pipeline metrics
    # Uptime, version, etc.

    uptime = time.time() - startup_time

    cache = get_cache_service()
    cache_stats = await cache.get_stats()

    pipeline = get_event_pipeline()
    pipeline_metrics = pipeline.get_metrics()

    return {
        "status": "healthy",
        "uptime_seconds": int(uptime),
        "version": "1.0.0",
        "dependencies": {
            "database": {
                "status": "healthy",
                "latency_ms": 5
            },
            "cache": {
                "status": "healthy",
                "hit_rate": cache_stats.hit_rate,
                "total_keys": cache_stats.total_keys
            },
            "event_pipeline": {
                "status": "healthy",
                "queue_size": pipeline_metrics.events_in_queue,
                "throughput": pipeline_metrics.throughput_per_second
            }
        }
    }
```

**Estimated**: 3-4 hours
**Priority**: 3 (After cache and pipeline)

---

## 🚀 Implementation Sequence

### Step 1: Cache Service (Day 1)
1. Create infrastructure/cache/ directory
2. Implement base.py (abstract interface)
3. Implement memory.py (memory backend)
4. Implement redis.py (Redis backend)
5. Implement service.py (facade with fallback)
6. Create services/cache_service.py (singleton)
7. Add config to settings
8. Write tests
9. Integrate with identity_resolver
10. Integrate with pathfinder

**Deliverable**: Working cache with Redis, 70%+ hit rates

### Step 2: Event Pipeline (Day 2-3)
1. Create infrastructure/events/ directory
2. Implement types.py (event dataclasses)
3. Implement processors/base.py
4. Implement processors/relationship.py
5. Implement processors/attestation.py
6. Implement pipeline.py
7. Create api/internal.py
8. Register internal router
9. Write tests
10. Update TypeScript indexer

**Deliverable**: Event pipeline processing firehose events

### Step 3: Health Checks (Day 3)
1. Create api/health.py
2. Move health endpoints from main.py
3. Add readiness checks
4. Add detailed diagnostics
5. Integrate with cache and pipeline
6. Write tests
7. Document for ops

**Deliverable**: Comprehensive health monitoring

---

## 📊 Success Criteria

### Must Have
- [ ] Cache service deployed with Redis
- [ ] 70%+ cache hit rate measured
- [ ] Event pipeline processing all firehose events
- [ ] <100ms average event processing
- [ ] Health checks show all systems
- [ ] Zero data loss in event processing
- [ ] All tests passing

### Nice to Have
- [ ] 85%+ cache hit rate
- [ ] <50ms event processing
- [ ] Monitoring dashboard
- [ ] Automated alerts

---

**Next**: Start implementation following this blueprint

