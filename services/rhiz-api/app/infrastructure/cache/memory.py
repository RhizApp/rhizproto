"""
In-memory cache backend

Used for development, testing, and as fallback when Redis unavailable
"""

import fnmatch
import sys
import time
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple

from .base import CacheBackend, CacheStats


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with TTL support"""

    def __init__(self, max_size: int = 10000):
        """
        Initialize memory cache

        Args:
            max_size: Maximum number of keys to store
        """
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._max_size = max_size
        self._stats = defaultdict(int)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            value, expiry = self._cache[key]
            # Check if expired
            if expiry is None or expiry > time.time():
                self._stats["hits"] += 1
                return value
            else:
                # Expired, delete it
                del self._cache[key]
                self._stats["misses"] += 1
                return None
        else:
            self._stats["misses"] += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        # Evict oldest entry if at max size
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Simple FIFO eviction
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        # Calculate expiry time
        expiry = time.time() + ttl if ttl else None

        self._cache[key] = (value, expiry)
        self._stats["sets"] += 1
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.get(key) is not None

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching glob pattern"""
        matching_keys = [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]

        for key in matching_keys:
            del self._cache[key]

        count = len(matching_keys)
        self._stats["deletes"] += count
        return count

    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        # Estimate memory usage (rough approximation)
        memory_bytes = sum(
            sys.getsizeof(k) + sys.getsizeof(v[0]) for k, v in self._cache.items()
        )

        return CacheStats(
            hits=self._stats["hits"],
            misses=self._stats["misses"],
            sets=self._stats["sets"],
            deletes=self._stats["deletes"],
            hit_rate=hit_rate,
            total_keys=len(self._cache),
            memory_usage_bytes=memory_bytes,
        )

    async def close(self) -> None:
        """Close and cleanup"""
        self._cache.clear()
        self._stats.clear()

