"""
Redis cache backend

Production-ready distributed caching with Redis
"""

import json
import logging
import pickle
from typing import Any, Optional

from redis.asyncio import Redis

from .base import CacheBackend, CacheStats

logger = logging.getLogger(__name__)


class RedisCacheBackend(CacheBackend):
    """Redis cache backend for production use"""

    def __init__(self, redis_url: str):
        """
        Initialize Redis cache

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379")
        """
        self._redis: Redis = Redis.from_url(
            redis_url, encoding="utf-8", decode_responses=False  # Handle binary data
        )
        self._stats_key = "cache:stats"
        logger.info(f"Redis cache backend initialized: {redis_url}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self._redis.get(key)
            if value:
                # Increment hit counter
                await self._redis.hincrby(self._stats_key, "hits", 1)

                # Try JSON first, fallback to pickle
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return pickle.loads(value)
            else:
                await self._redis.hincrby(self._stats_key, "misses", 1)
                return None

        except Exception as e:
            logger.error(f"Redis get error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            # Try JSON serialization first (more efficient)
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fallback to pickle for complex objects
                serialized = pickle.dumps(value)

            if ttl:
                await self._redis.setex(key, ttl, serialized)
            else:
                await self._redis.set(key, serialized)

            await self._redis.hincrby(self._stats_key, "sets", 1)
            return True

        except Exception as e:
            logger.error(f"Redis set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            count = await self._redis.delete(key)
            if count > 0:
                await self._redis.hincrby(self._stats_key, "deletes", 1)
                return True
            return False

        except Exception as e:
            logger.error(f"Redis delete error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key '{key}': {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern using SCAN"""
        deleted = 0

        try:
            # Use SCAN to avoid blocking on large keysets
            async for key in self._redis.scan_iter(match=pattern):
                await self._redis.delete(key)
                deleted += 1

            if deleted > 0:
                await self._redis.hincrby(self._stats_key, "deletes", deleted)

            return deleted

        except Exception as e:
            logger.error(f"Redis clear_pattern error for pattern '{pattern}': {e}")
            return 0

    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        try:
            stats_data = await self._redis.hgetall(self._stats_key)

            # Decode bytes to int
            hits = int(stats_data.get(b"hits", 0))
            misses = int(stats_data.get(b"misses", 0))
            sets = int(stats_data.get(b"sets", 0))
            deletes = int(stats_data.get(b"deletes", 0))

            total_requests = hits + misses
            hit_rate = hits / total_requests if total_requests > 0 else 0.0

            # Get database size and memory usage
            total_keys = await self._redis.dbsize()
            info = await self._redis.info("memory")
            memory_bytes = info.get("used_memory", 0)

            return CacheStats(
                hits=hits,
                misses=misses,
                sets=sets,
                deletes=deletes,
                hit_rate=hit_rate,
                total_keys=total_keys,
                memory_usage_bytes=memory_bytes,
            )

        except Exception as e:
            logger.error(f"Redis get_stats error: {e}")
            return CacheStats(
                hits=0, misses=0, sets=0, deletes=0, hit_rate=0.0, total_keys=0, memory_usage_bytes=0
            )

    async def close(self) -> None:
        """Close Redis connection"""
        try:
            await self._redis.close()
            logger.info("Redis cache backend closed")
        except Exception as e:
            logger.error(f"Redis close error: {e}")

