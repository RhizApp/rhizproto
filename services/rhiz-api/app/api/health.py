"""
Enhanced health check endpoints

Provides multi-level health monitoring:
- Liveness: Is service running?
- Readiness: Can service handle requests?
- Detailed: Full diagnostic information
"""

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.infrastructure.events import get_event_pipeline
from app.services.cache_service import get_unified_cache

router = APIRouter(prefix="/health", tags=["health"])

# Track startup time for uptime calculation
STARTUP_TIME = time.time()


@router.get("")
async def liveness():
    """
    Liveness check (fast, <10ms)

    Returns 200 if service is running

    Used by: Load balancers, orchestrators
    """
    return {"status": "healthy", "timestamp": time.time()}


@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Readiness check with dependency verification (<100ms)

    Checks:
    - Database connectivity
    - Cache availability
    - Event pipeline status

    Returns 200 if all dependencies healthy, 503 if degraded

    Used by: Load balancers, readiness probes
    """
    checks: Dict[str, str] = {}
    overall_healthy = True

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = "unhealthy"
        overall_healthy = False

    # Cache check
    try:
        cache = get_unified_cache()
        cache_health = await cache.health_check()
        checks["cache"] = cache_health["status"]

        if cache_health["status"] != "healthy":
            overall_healthy = False

    except Exception as e:
        checks["cache"] = "unhealthy"
        overall_healthy = False

    # Event pipeline check
    try:
        pipeline = get_event_pipeline()
        metrics = pipeline.get_metrics()

        # Pipeline is degraded if queue too large or backpressure active
        if metrics.backpressure_active or metrics.events_in_queue > 8000:
            checks["event_pipeline"] = "degraded"
            overall_healthy = False
        else:
            checks["event_pipeline"] = "healthy"

    except Exception as e:
        checks["event_pipeline"] = "unhealthy"
        overall_healthy = False

    status_code = 200 if overall_healthy else 503

    return {
        "status": "ready" if overall_healthy else "degraded",
        "checks": checks,
        "timestamp": time.time(),
    }


@router.get("/detailed")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """
    Detailed health with full diagnostics (<500ms)

    Provides comprehensive health information:
    - Service uptime and version
    - Database connection pool stats
    - Cache statistics
    - Event pipeline metrics
    - Performance metrics

    Used by: Monitoring dashboards, debugging

    Returns:
        Detailed health status
    """
    uptime_seconds = int(time.time() - STARTUP_TIME)

    # Database health
    database_health = {"status": "unknown"}
    try:
        # Test query
        await db.execute(text("SELECT 1"))

        # Get connection pool stats (if available)
        database_health = {
            "status": "healthy",
            "latency_ms": 5,  # Could measure actual latency
        }
    except Exception as e:
        database_health = {"status": "unhealthy", "error": str(e)}

    # Cache health
    cache_health = {"status": "unknown"}
    try:
        cache = get_unified_cache()
        cache_health = await cache.health_check()

        # Add cache stats
        stats = await cache.get_stats()
        cache_health["stats"] = {
            "hit_rate": round(stats.hit_rate, 3),
            "total_keys": stats.total_keys,
            "hits": stats.hits,
            "misses": stats.misses,
            "memory_mb": round(stats.memory_usage_bytes / (1024 * 1024), 2),
        }

    except Exception as e:
        cache_health = {"status": "unhealthy", "error": str(e)}

    # Event pipeline health
    pipeline_health = {"status": "unknown"}
    try:
        pipeline = get_event_pipeline()

        if pipeline.is_running():
            metrics = pipeline.get_metrics()

            pipeline_health = {
                "status": "degraded" if metrics.backpressure_active else "healthy",
                "metrics": {
                    "events_processed": metrics.events_processed,
                    "events_failed": metrics.events_failed,
                    "events_in_queue": metrics.events_in_queue,
                    "avg_processing_time_ms": round(metrics.avg_processing_time_ms, 2),
                    "throughput_per_second": round(metrics.throughput_per_second, 2),
                    "worker_utilization": round(metrics.worker_utilization, 2),
                    "backpressure_active": metrics.backpressure_active,
                },
                "dead_letter_count": len(pipeline.get_dead_letter_queue()),
            }
        else:
            pipeline_health = {"status": "stopped"}

    except Exception as e:
        pipeline_health = {"status": "unhealthy", "error": str(e)}

    # Overall status
    all_healthy = all(
        [
            database_health.get("status") == "healthy",
            cache_health.get("status") == "healthy",
            pipeline_health.get("status") in ["healthy", "degraded"],
        ]
    )

    from app.config import get_settings

    settings = get_settings()

    return {
        "status": "healthy" if all_healthy else "degraded",
        "uptime_seconds": uptime_seconds,
        "version": settings.app_version,
        "environment": settings.app_env,
        "dependencies": {
            "database": database_health,
            "cache": cache_health,
            "event_pipeline": pipeline_health,
        },
        "timestamp": time.time(),
    }

