"""
Cache infrastructure

Unified caching with adapter pattern supporting multiple backends
"""

from .base import CacheBackend, CacheStats
from .memory import MemoryCacheBackend
from .redis import RedisCacheBackend
from .service import CacheService

__all__ = [
    "CacheBackend",
    "CacheStats",
    "MemoryCacheBackend",
    "RedisCacheBackend",
    "CacheService",
]

