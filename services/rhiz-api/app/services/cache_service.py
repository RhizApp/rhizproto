"""
Redis caching service for high-performance graph queries
Implements intelligent caching strategies for trust metrics and pathfinding
"""

import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import settings


class CacheService:
    """
    High-performance caching service using Redis
    
    Provides caching for:
    - Trust metrics
    - Graph pathfinding results
    - Entity data
    - Relationship contexts
    """
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._connected = False
    
    async def connect(self):
        """Initialize Redis connection"""
        if not self._connected:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            self._connected = True
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self._connected = False
    
    # Trust Metrics Caching
    
    async def cache_trust_metrics(
        self, 
        entity_id: str, 
        metrics: Dict[str, Any], 
        ttl: int = 3600
    ):
        """Cache trust metrics for an entity"""
        await self.connect()
        
        cache_key = f"trust_metrics:{entity_id}"
        
        # Add cache metadata
        cache_data = {
            **metrics,
            "cached_at": datetime.utcnow().isoformat(),
            "entity_id": entity_id
        }
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(cache_data, default=str)
        )
    
    async def get_trust_metrics(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached trust metrics"""
        await self.connect()
        
        cache_key = f"trust_metrics:{entity_id}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def invalidate_trust_metrics(self, entity_id: str):
        """Invalidate trust metrics cache for an entity"""
        await self.connect()
        
        cache_key = f"trust_metrics:{entity_id}"
        await self.redis.delete(cache_key)
    
    # Graph Pathfinding Caching
    
    async def cache_path_result(
        self,
        from_entity: str,
        to_entity: str,
        path_result: Dict[str, Any],
        query_params: Dict[str, Any],
        ttl: int = 1800  # 30 minutes
    ):
        """Cache pathfinding results"""
        await self.connect()
        
        # Create deterministic cache key from query parameters
        cache_key = self._generate_path_cache_key(
            from_entity, to_entity, query_params
        )
        
        cache_data = {
            **path_result,
            "cached_at": datetime.utcnow().isoformat(),
            "query_params": query_params
        }
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(cache_data, default=str)
        )
        
        # Also cache reverse path if bidirectional
        if query_params.get("bidirectional", True):
            reverse_key = self._generate_path_cache_key(
                to_entity, from_entity, query_params
            )
            
            # Create reverse path result
            reverse_result = self._reverse_path_result(path_result)
            reverse_cache_data = {
                **reverse_result,
                "cached_at": datetime.utcnow().isoformat(),
                "query_params": query_params
            }
            
            await self.redis.setex(
                reverse_key,
                ttl,
                json.dumps(reverse_cache_data, default=str)
            )
    
    async def get_cached_path(
        self,
        from_entity: str,
        to_entity: str,
        query_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached pathfinding result"""
        await self.connect()
        
        cache_key = self._generate_path_cache_key(
            from_entity, to_entity, query_params
        )
        
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            result = json.loads(cached_data)
            
            # Check if cache is still fresh enough for this query
            cached_at = datetime.fromisoformat(result["cached_at"])
            max_age = query_params.get("max_cache_age", 1800)  # 30 min default
            
            if (datetime.utcnow() - cached_at).seconds <= max_age:
                return result
            else:
                # Cache expired, delete it
                await self.redis.delete(cache_key)
        
        return None
    
    def _generate_path_cache_key(
        self,
        from_entity: str,
        to_entity: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Generate deterministic cache key for pathfinding queries"""
        # Create normalized parameter string
        normalized_params = {
            "max_hops": query_params.get("max_hops", 6),
            "min_strength": query_params.get("min_strength", 0.5),
            "relationship_types": sorted(query_params.get("relationship_types", [])),
            "exclude_entities": sorted(query_params.get("exclude_entities", [])),
            "algorithm": query_params.get("algorithm", "astar")
        }
        
        param_string = json.dumps(normalized_params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
        
        return f"path:{from_entity}:{to_entity}:{param_hash}"
    
    def _reverse_path_result(self, path_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create reverse path from cached result"""
        if not path_result.get("hops"):
            return path_result
        
        # Reverse the hops
        reversed_hops = []
        for hop in reversed(path_result["hops"]):
            reversed_hops.append({
                "from_entity": hop["to_entity"],
                "to_entity": hop["from_entity"],
                "relationship_id": hop["relationship_id"],
                "strength": hop["strength"]
            })
        
        return {
            **path_result,
            "from_entity": path_result["to_entity"],
            "to_entity": path_result["from_entity"],
            "hops": reversed_hops
        }
    
    # Entity Caching
    
    async def cache_entity(
        self, 
        entity_id: str, 
        entity_data: Dict[str, Any], 
        ttl: int = 7200  # 2 hours
    ):
        """Cache entity data"""
        await self.connect()
        
        cache_key = f"entity:{entity_id}"
        
        cache_data = {
            **entity_data,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(cache_data, default=str)
        )
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached entity data"""
        await self.connect()
        
        cache_key = f"entity:{entity_id}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def invalidate_entity(self, entity_id: str):
        """Invalidate entity cache"""
        await self.connect()
        
        cache_key = f"entity:{entity_id}"
        await self.redis.delete(cache_key)
    
    # Neighbors Caching
    
    async def cache_neighbors(
        self,
        entity_id: str,
        neighbors: List[Dict[str, Any]],
        query_params: Dict[str, Any],
        ttl: int = 900  # 15 minutes
    ):
        """Cache entity neighbors"""
        await self.connect()
        
        param_hash = hashlib.md5(
            json.dumps(query_params, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        cache_key = f"neighbors:{entity_id}:{param_hash}"
        
        cache_data = {
            "neighbors": neighbors,
            "query_params": query_params,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(cache_data, default=str)
        )
    
    async def get_cached_neighbors(
        self,
        entity_id: str,
        query_params: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached neighbors"""
        await self.connect()
        
        param_hash = hashlib.md5(
            json.dumps(query_params, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        cache_key = f"neighbors:{entity_id}:{param_hash}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            result = json.loads(cached_data)
            return result["neighbors"]
        return None
    
    # Semantic Search Caching
    
    async def cache_similar_relationships(
        self,
        query_embedding: List[float],
        results: List[Dict[str, Any]],
        filter_params: Dict[str, Any],
        ttl: int = 3600
    ):
        """Cache semantic search results"""
        await self.connect()
        
        # Create hash from embedding and filters
        embedding_hash = hashlib.md5(
            json.dumps(query_embedding).encode()
        ).hexdigest()[:12]
        
        filter_hash = hashlib.md5(
            json.dumps(filter_params, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        cache_key = f"semantic:{embedding_hash}:{filter_hash}"
        
        cache_data = {
            "results": results,
            "filter_params": filter_params,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(cache_data, default=str)
        )
    
    # Cache Management
    
    async def invalidate_entity_related_caches(self, entity_id: str):
        """Invalidate all caches related to an entity"""
        await self.connect()
        
        # Find and delete all related cache keys
        patterns = [
            f"trust_metrics:{entity_id}",
            f"entity:{entity_id}",
            f"neighbors:{entity_id}:*",
            f"path:{entity_id}:*",
            f"path:*:{entity_id}:*"
        ]
        
        for pattern in patterns:
            if "*" in pattern:
                # Use SCAN for pattern matching
                async for key in self.redis.scan_iter(match=pattern):
                    await self.redis.delete(key)
            else:
                await self.redis.delete(pattern)
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache usage statistics"""
        await self.connect()
        
        # Get Redis info
        info = await self.redis.info()
        
        # Count keys by type
        key_counts = {}
        async for key in self.redis.scan_iter():
            key_type = key.split(":")[0]
            key_counts[key_type] = key_counts.get(key_type, 0) + 1
        
        return {
            "total_keys": info.get("db0", {}).get("keys", 0),
            "memory_usage": info.get("used_memory_human", "0B"),
            "key_counts": key_counts,
            "hit_rate": info.get("keyspace_hits", 0) / max(
                info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
            )
        }
    
    async def warm_cache_for_entity(self, entity_id: str):
        """Pre-warm cache with commonly accessed data for an entity"""
        # This would typically be called when an entity is frequently accessed
        # Implementation would load trust metrics, neighbors, etc.
        pass
    
    async def cleanup_expired_keys(self):
        """Clean up expired keys (Redis handles this automatically, but useful for monitoring)"""
        await self.connect()
        
        # Get expired keys count for monitoring
        info = await self.redis.info()
        return {
            "expired_keys": info.get("expired_keys", 0),
            "evicted_keys": info.get("evicted_keys", 0)
        }


# Global cache instance
cache_service = CacheService()


# Decorator for caching function results
def cache_result(ttl: int = 3600, key_prefix: str = "func"):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            key_hash = hashlib.md5(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()[:12]
            
            cache_key = f"{key_prefix}:{func.__name__}:{key_hash}"
            
            # Try to get from cache
            await cache_service.connect()
            cached_result = await cache_service.redis.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            await cache_service.redis.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )
            
            return result
        
        return wrapper
    return decorator