# Protocol Improvements V2 - Enhanced Plan

**Version**: 2.0 (Improved)
**Date**: October 23, 2025
**Status**: Planning → Implementation Ready

---

## 🎯 Improvements Over V1

### What's Better in V2:

1. **Integration Analysis**: Analyzed existing code to avoid duplication
2. **Concrete Architecture**: Specific file locations and integration points
3. **Dependency Management**: Clear dependencies between components
4. **Performance Targets**: Measurable KPIs for each feature
5. **Risk Mitigation**: Identified blockers and fallback strategies

### Current State Analysis:

**✅ What Exists:**
- Basic LRU cache in `identity_resolver.py`
- Simple in-memory cache in `pathfinder.py`
- Firehose indexer (TypeScript) with callback pattern
- Health check endpoints (basic)

**❌ What's Missing:**
- Unified cache service (Redis-backed)
- Event pipeline with backpressure handling
- Real-time processing architecture
- Comprehensive health monitoring
- Background task system

---

## 📊 Phase 1: Infrastructure Foundation (PRIORITY 1)

### 1. Unified Cache Service

**File**: `services/rhiz-api/app/services/cache_service.py`

**Problem**: Current state has scattered caching:
- `identity_resolver.py`: LRU cache (1000 entries max)
- `pathfinder.py`: In-memory dict cache
- No Redis support
- No TTL management
- No cache invalidation patterns

**Solution**:
```python
class CacheService:
    """
    Unified caching with adapter pattern

    Backends:
    - Memory: Development, testing
    - Redis: Production (distributed)

    Features:
    - TTL management per key
    - Pattern-based clearing (e.g., "trust:*")
    - Automatic serialization (JSON/pickle)
    - Fallback to memory if Redis unavailable
    - Statistics tracking
    """

    def __init__(self, backend: str = "memory", redis_url: Optional[str] = None)
    async def get(self, key: str) -> Optional[Any]
    async def set(self, key: str, value: Any, ttl: Optional[int] = None)
    async def delete(self, key: str)
    async def clear_pattern(self, pattern: str)
    async def get_stats() -> CacheStats
```

**Integration Points**:
- `identity_resolver.py`: Replace LRU with unified cache
- `pathfinder.py`: Replace dict cache with unified cache
- `trust_engine.py`: Add caching for trust calculations
- `conviction.py`: Cache conviction scores

**Cache Strategy**:
```python
# Trust Metrics: 24hr TTL (recalculated daily)
cache.set(f"trust:metrics:{did}", metrics, ttl=86400)

# Graph Paths: 1hr TTL (relationships change less frequently)
cache.set(f"graph:path:{from_did}:{to_did}", path, ttl=3600)

# Conviction Scores: Invalidate on new attestation
cache.set(f"conviction:{uri}", score, ttl=None)  # Manual invalidation

# Entity Profiles: 6hr TTL
cache.set(f"entity:{did}", profile, ttl=21600)

# DID Resolution: 7 day TTL (DIDs rarely change)
cache.set(f"did:resolve:{did}", identity, ttl=604800)
```

**Performance Targets**:
- Cache hit rate >70% for trust scores
- <5ms latency for cache hits
- >90% reduction in database queries for paths
- <1ms latency for Redis operations

**Implementation Steps**:
1. Create `cache_service.py` with adapter pattern
2. Add Redis client initialization
3. Add memory fallback
4. Add TTL management
5. Add pattern-based clearing
6. Add statistics tracking
7. Integrate with existing services
8. Add configuration to `config.py`
9. Write tests
10. Deploy with Redis instance

**Estimated**: 5-6 hours
**Dependencies**: None
**Blocker Risk**: Low

---

### 2. Real-Time Event Pipeline

**Files**:
- `services/rhiz-api/app/services/event_pipeline.py`
- `services/rhiz-api/app/services/event_processors/`

**Problem**: Current firehose indexer is synchronous:
- TypeScript callback-based
- No backpressure handling
- No event queuing
- Single-threaded processing
- No retry logic
- No event priority

**Solution**: Event-driven pipeline with async workers

```python
class EventPipeline:
    """
    Real-time event processing pipeline

    Architecture:
    - Async queue with bounded size
    - Multi-worker processing pool
    - Backpressure handling (reject when full)
    - Priority queues (attestations > relationships)
    - Retry with exponential backoff
    - Dead letter queue for failed events
    - Metrics and monitoring
    """

    def __init__(self, max_queue_size: int = 10000, num_workers: int = 10)
    async def enqueue(self, event: ProtocolEvent, priority: int = 0)
    async def start()
    async def stop()
    def get_metrics() -> PipelineMetrics
```

**Event Types**:
```python
class EventType(Enum):
    RELATIONSHIP_CREATED = "relationship.created"
    RELATIONSHIP_UPDATED = "relationship.updated"
    RELATIONSHIP_DELETED = "relationship.deleted"
    ATTESTATION_CREATED = "attestation.created"
    ENTITY_PROFILE_UPDATED = "entity.profile.updated"
    TRUST_SCORE_INVALIDATED = "trust.invalidated"
```

**Event Flow**:
```
Firehose (TypeScript)
    ↓ HTTP POST to /internal/events
Python Event Pipeline
    ↓ Queue with priority
Worker Pool (10 workers)
    ↓ Process in parallel
Stages:
    1. Validation
    2. Enrichment (optional)
    3. Database write
    4. Cache invalidation
    5. Metrics update
    6. Webhook notification (future)
```

**Integration with Firehose**:
```typescript
// services/rhiz-atproto/src/indexer/relationship_indexer.ts
async onRelationshipCreated(relationship: IndexedRelationship) {
  // Instead of direct DB write, enqueue event
  await axios.post('http://python-api:8000/internal/events', {
    type: 'relationship.created',
    data: relationship,
    priority: 1
  });
}
```

**Performance Targets**:
- Process 1000+ events/second
- <100ms latency per event
- >99.9% success rate
- <10 events in queue under normal load
- Backpressure threshold at 8000 events

**Implementation Steps**:
1. Create event pipeline architecture
2. Add async queue with priority
3. Add worker pool management
4. Create event processors for each type
5. Add retry logic with dead letter queue
6. Add metrics tracking
7. Create internal API endpoint `/internal/events`
8. Update TypeScript indexer to use HTTP
9. Add monitoring dashboard
10. Load test with simulated firehose

**Estimated**: 8-10 hours
**Dependencies**: Unified cache service (for invalidation)
**Blocker Risk**: Medium (requires coordination with TS service)

---

### 3. Enhanced Health Check System

**File**: `services/rhiz-api/app/api/health.py` (enhance existing)

**Problem**: Current health checks are basic:
- Only liveness check
- No dependency monitoring
- No detailed diagnostics

**Solution**: Comprehensive health monitoring

```python
class HealthCheckService:
    """
    Multi-level health checks

    Levels:
    - Liveness: Is service running?
    - Readiness: Can service handle requests?
    - Detailed: Full diagnostic information
    """

    async def check_liveness() -> HealthStatus
    async def check_readiness() -> ReadinessStatus
    async def check_detailed() -> DetailedHealth
```

**Health Checks**:
```python
# GET /health - Liveness (fast, <10ms)
{
  "status": "healthy",
  "timestamp": "2025-10-23T12:00:00Z"
}

# GET /health/ready - Readiness (<100ms)
{
  "status": "ready",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "firehose": "healthy"
  },
  "timestamp": "2025-10-23T12:00:00Z"
}

# GET /health/detailed - Full diagnostics (<500ms)
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "version": "1.0.0",
  "dependencies": {
    "database": {
      "status": "healthy",
      "latency_ms": 5,
      "connections": {
        "active": 10,
        "idle": 5,
        "max": 20
      }
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1,
      "memory_used_mb": 128,
      "hit_rate": 0.85
    },
    "firehose": {
      "status": "healthy",
      "events_per_second": 50,
      "lag_seconds": 0.5
    }
  },
  "metrics": {
    "requests_per_second": 100,
    "avg_response_time_ms": 25,
    "error_rate": 0.001,
    "event_queue_size": 5
  },
  "timestamp": "2025-10-23T12:00:00Z"
}
```

**Performance Targets**:
- Liveness <10ms
- Readiness <100ms
- Detailed <500ms
- Dependency checks in parallel

**Implementation Steps**:
1. Enhance existing health endpoints
2. Add database health check
3. Add Redis health check
4. Add firehose lag monitoring
5. Add metrics aggregation
6. Add parallel dependency checks
7. Add caching for detailed checks (10s TTL)
8. Add alerting hooks
9. Write tests
10. Document for ops team

**Estimated**: 3-4 hours
**Dependencies**: Unified cache service, Event pipeline
**Blocker Risk**: Low

---

## 📈 Phase 1 Success Metrics

### Performance
- [ ] Cache hit rate >70%
- [ ] Event processing <100ms avg
- [ ] Health checks <100ms for readiness
- [ ] Graph queries 3-5x faster

### Reliability
- [ ] Event pipeline 99.9%+ success rate
- [ ] Zero dropped events under normal load
- [ ] Graceful degradation on Redis failure
- [ ] Automatic reconnection on firehose disconnect

### Observability
- [ ] Health dashboard shows all systems
- [ ] Metrics tracked for all operations
- [ ] Cache statistics visible
- [ ] Event pipeline metrics visible

---

## 🔧 Implementation Order

### Week 1: Days 1-2
**Task**: Unified Cache Service (5-6h)
- Create cache service with adapter pattern
- Add Redis and memory backends
- Integrate with existing services
- Write tests

**Deliverables**:
- `app/services/cache_service.py`
- Redis configuration
- Integration with identity_resolver, pathfinder
- Tests passing

### Week 1: Days 3-5
**Task**: Event Pipeline (8-10h)
- Create event pipeline architecture
- Add worker pool and queue
- Create event processors
- Integrate with firehose

**Deliverables**:
- `app/services/event_pipeline.py`
- Event processors for each type
- Internal API endpoint
- Updated TypeScript indexer

### Week 1: Day 5
**Task**: Enhanced Health Checks (3-4h)
- Enhance health endpoints
- Add dependency monitoring
- Add metrics aggregation

**Deliverables**:
- Enhanced `/health/*` endpoints
- Monitoring dashboard data
- Documentation

---

## 🧪 Testing Strategy

### Unit Tests
- Cache service: memory and Redis backends
- Event pipeline: queue, workers, retry logic
- Event processors: each event type
- Health checks: all dependency checks

### Integration Tests
- Cache with real Redis instance
- Event pipeline with simulated firehose
- End-to-end event flow
- Health checks with all dependencies

### Load Tests
- 1000 events/second sustained
- 10,000 concurrent cache operations
- Cache hit rate under load
- Event queue backpressure handling

### Chaos Tests
- Redis failure and recovery
- Database connection loss
- Firehose disconnect
- Worker crash handling

---

## 🚀 Deployment Strategy

### Configuration
```yaml
# config.yaml
cache:
  backend: redis  # or memory
  redis_url: redis://localhost:6379
  default_ttl: 3600

event_pipeline:
  max_queue_size: 10000
  num_workers: 10
  backpressure_threshold: 8000
  retry_max_attempts: 3

health:
  detailed_cache_ttl: 10
  dependency_timeout: 5
```

### Deployment Steps
1. Deploy Redis instance (Railway/separate)
2. Update environment variables
3. Deploy Python API with new code
4. Deploy TypeScript indexer with HTTP integration
5. Monitor health endpoints
6. Verify metrics
7. Load test in staging
8. Gradual rollout to production

### Rollback Plan
- Redis failure → automatic fallback to memory
- Event pipeline issues → direct DB writes (bypass queue)
- Health check failures → return to basic health

---

## 📊 Monitoring & Alerts

### Metrics to Track
- Cache hit rate (target >70%)
- Event processing latency (target <100ms)
- Event queue size (alert if >8000)
- Worker pool utilization
- Database connection pool
- Redis memory usage
- Health check response times

### Alerts
- Cache hit rate <50% (warning)
- Event queue >8000 (critical)
- Event processing >500ms (warning)
- Redis unavailable (warning, auto-fallback)
- Database unavailable (critical)
- Worker crash (warning)

---

## 🎯 Phase 2 Preview (Not Implemented Yet)

Based on Phase 1 learnings, Phase 2 will add:

1. **Entity Enrichment Orchestrator** (5-6h)
   - Leverage event pipeline for enrichment triggers
   - Use cache service for enrichment results

2. **Relationship Predictions** (6-8h)
   - Use cached trust metrics for predictions
   - Event-driven prediction updates

3. **Background Tasks** (5-6h)
   - Use event pipeline for task queuing
   - Scheduled via cron or similar

---

## ✅ Definition of Done

Phase 1 is complete when:

- [ ] Unified cache service deployed with Redis
- [ ] 70%+ cache hit rate for trust scores
- [ ] Event pipeline processing firehose events
- [ ] <100ms average event processing time
- [ ] Enhanced health checks showing all systems
- [ ] All tests passing (unit, integration, load)
- [ ] Documentation updated
- [ ] Monitoring dashboard live
- [ ] Zero production incidents for 1 week

---

**Next**: Create V3 (Refined Implementation Plan) with exact code structure

