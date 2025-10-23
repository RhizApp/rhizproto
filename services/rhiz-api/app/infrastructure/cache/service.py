"""
Unified cache service with automatic fallback

Provides a single interface to caching with adapter pattern
"""

import logging
from typing import Any, Dict, Optional

from .base import CacheBackend, CacheStats
from .memory import MemoryCacheBackend
from .redis import RedisCacheBackend

logger = logging.getLogger(__name__)


class CacheService:
    """
    Unified caching service with automatic fallback

    Usage:
        cache = CacheService(backend="redis", redis_url="redis://localhost:6379")
        await cache.set("trust:alice", {"score": 88}, ttl=3600)
        score = await cache.get("trust:alice")

    Features:
    - Adapter pattern (memory/Redis)
    - Automatic fallback to memory if Redis fails
    - TTL management
    - Pattern-based clearing
    - Statistics tracking
    """

    def __init__(
        self, backend: str = "memory", redis_url: Optional[str] = None, fallback_to_memory: bool = True
    ):
        """
        Initialize cache service

        Args:
            backend: Cache backend ("memory" or "redis")
            redis_url: Redis connection URL (required for redis backend)
            fallback_to_memory: Enable memory fallback if Redis fails
        """
        self._backend: CacheBackend
        self._fallback: Optional[CacheBackend] = None

        if backend == "redis":
            try:
                self._backend = RedisCacheBackend(redis_url or "redis://localhost:6379")

                if fallback_to_memory:
                    self._fallback = MemoryCacheBackend()
                    logger.info("Cache service initialized with Redis (memory fallback enabled)")
                else:
                    logger.info("Cache service initialized with Redis (no fallback)")

            except Exception as e:
                logger.warning(f"Redis initialization failed, using memory backend: {e}")
                self._backend = MemoryCacheBackend()
        else:
            self._backend = MemoryCacheBackend()
            logger.info("Cache service initialized with memory backend")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with automatic fallback

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            return await self._backend.get(key)
        except Exception as e:
            logger.error(f"Cache backend error, trying fallback: {e}")
            if self._fallback:
                try:
                    return await self._fallback.get(key)
                except Exception as fallback_error:
                    logger.error(f"Fallback cache error: {fallback_error}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            success = await self._backend.set(key, value, ttl)

            # Also set in fallback cache for redundancy
            if success and self._fallback:
                try:
                    await self._fallback.set(key, value, ttl)
                except Exception as e:
                    logger.warning(f"Failed to sync to fallback cache: {e}")

            return success

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        success = await self._backend.delete(key)

        # Also delete from fallback
        if self._fallback:
            try:
                await self._fallback.delete(key)
            except Exception as e:
                logger.warning(f"Failed to delete from fallback cache: {e}")

        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self._backend.exists(key)

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Glob pattern (e.g., "trust:*", "graph:path:*")

        Returns:
            Number of keys cleared
        """
        count = await self._backend.clear_pattern(pattern)

        # Also clear from fallback
        if self._fallback:
            try:
                await self._fallback.clear_pattern(pattern)
            except Exception as e:
                logger.warning(f"Failed to clear pattern from fallback: {e}")

        return count

    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return await self._backend.get_stats()

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache

        Returns:
            Health status dict
        """
        try:
            test_key = "health:check:test"
            test_value = "ok"

            # Test write
            await self._backend.set(test_key, test_value, ttl=1)

            # Test read
            value = await self._backend.get(test_key)

            # Test delete
            await self._backend.delete(test_key)

            # Get stats
            stats = await self.get_stats()

            return {
                "status": "healthy" if value == test_value else "degraded",
                "backend": self._backend.__class__.__name__,
                "has_fallback": self._fallback is not None,
                "hit_rate": stats.hit_rate,
                "total_keys": stats.total_keys,
                "memory_usage_mb": stats.memory_usage_bytes / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "has_fallback": self._fallback is not None}

    async def close(self) -> None:
        """Close all cache connections"""
        await self._backend.close()

        if self._fallback:
            await self._fallback.close()

        logger.info("Cache service closed")

