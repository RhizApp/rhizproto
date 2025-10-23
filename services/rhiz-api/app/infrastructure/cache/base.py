"""
Abstract cache backend interface

Defines the contract that all cache backends must implement
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CacheStats:
    """Cache statistics"""

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
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = no expiration)

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired
        """
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching glob pattern

        Args:
            pattern: Glob pattern (e.g., "trust:*", "graph:path:*")

        Returns:
            Number of keys cleared
        """
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """
        Get cache statistics

        Returns:
            CacheStats with hit rate, key count, memory usage, etc.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close connections and cleanup resources
        """
        pass

