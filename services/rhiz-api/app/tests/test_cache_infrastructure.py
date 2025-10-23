"""
Tests for unified cache infrastructure

Tests memory and Redis backends with adapter pattern
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.infrastructure.cache import (
    CacheService,
    MemoryCacheBackend,
    RedisCacheBackend,
    CacheStats,
)


class TestMemoryCacheBackend:
    """Tests for memory cache backend"""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test basic set and get"""
        cache = MemoryCacheBackend()

        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")

        assert value == "test_value"
        await cache.close()

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        """Test TTL expiration"""
        cache = MemoryCacheBackend()

        await cache.set("test_key", "test_value", ttl=1)
        value1 = await cache.get("test_key")
        assert value1 == "test_value"

        # Wait for expiration
        import asyncio

        await asyncio.sleep(1.1)

        value2 = await cache.get("test_key")
        assert value2 is None
        await cache.close()

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test key deletion"""
        cache = MemoryCacheBackend()

        await cache.set("test_key", "test_value")
        deleted = await cache.delete("test_key")

        assert deleted is True
        assert await cache.get("test_key") is None
        await cache.close()

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test key existence check"""
        cache = MemoryCacheBackend()

        await cache.set("test_key", "test_value")

        assert await cache.exists("test_key") is True
        assert await cache.exists("nonexistent") is False
        await cache.close()

    @pytest.mark.asyncio
    async def test_clear_pattern(self):
        """Test pattern-based clearing"""
        cache = MemoryCacheBackend()

        await cache.set("trust:alice", 88)
        await cache.set("trust:bob", 92)
        await cache.set("graph:path", "data")

        count = await cache.clear_pattern("trust:*")

        assert count == 2
        assert await cache.get("trust:alice") is None
        assert await cache.get("trust:bob") is None
        assert await cache.get("graph:path") == "data"
        await cache.close()

    @pytest.mark.asyncio
    async def test_max_size_eviction(self):
        """Test eviction when max size reached"""
        cache = MemoryCacheBackend(max_size=5)

        # Fill cache to max
        for i in range(5):
            await cache.set(f"key_{i}", f"value_{i}")

        # Add one more - should evict oldest
        await cache.set("key_new", "value_new")

        # Oldest (key_0) should be evicted
        assert await cache.get("key_0") is None
        assert await cache.get("key_new") == "value_new"
        await cache.close()

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test cache statistics"""
        cache = MemoryCacheBackend()

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.get("key1")  # Hit
        await cache.get("nonexistent")  # Miss

        stats = await cache.get_stats()

        assert stats.sets == 2
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.total_keys == 2
        assert 0.0 < stats.hit_rate < 1.0
        await cache.close()


class TestCacheService:
    """Tests for unified cache service"""

    @pytest.mark.asyncio
    async def test_memory_backend_initialization(self):
        """Test initialization with memory backend"""
        cache = CacheService(backend="memory")

        await cache.set("test", "value")
        value = await cache.get("test")

        assert value == "value"
        await cache.close()

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """Test automatic fallback to memory"""
        # Invalid Redis URL should fallback to memory
        cache = CacheService(backend="redis", redis_url="redis://invalid:9999", fallback_to_memory=True)

        await cache.set("test", "value")
        value = await cache.get("test")

        # Should work via fallback
        assert value == "value"
        await cache.close()

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test cache health check"""
        cache = CacheService(backend="memory")

        health = await cache.health_check()

        assert health["status"] == "healthy"
        assert "backend" in health
        assert "hit_rate" in health
        await cache.close()

    @pytest.mark.asyncio
    async def test_pattern_clearing(self):
        """Test clearing keys by pattern"""
        cache = CacheService(backend="memory")

        await cache.set("prefix:key1", "value1")
        await cache.set("prefix:key2", "value2")
        await cache.set("other:key3", "value3")

        count = await cache.clear_pattern("prefix:*")

        assert count == 2
        assert await cache.get("other:key3") == "value3"
        await cache.close()

    @pytest.mark.asyncio
    async def test_complex_objects(self):
        """Test caching complex Python objects"""
        cache = CacheService(backend="memory")

        complex_obj = {"nested": {"data": [1, 2, 3]}, "score": 88, "metadata": {"cached": True}}

        await cache.set("complex", complex_obj)
        retrieved = await cache.get("complex")

        assert retrieved == complex_obj
        assert retrieved["nested"]["data"] == [1, 2, 3]
        await cache.close()

