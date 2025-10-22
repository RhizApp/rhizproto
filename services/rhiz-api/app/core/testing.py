"""
Comprehensive testing infrastructure for Rhiz Protocol
Provides test utilities, fixtures, and standardized testing patterns
"""

import asyncio
import pytest
from typing import Any, Dict, List, Optional, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import RhizProtocolSettings
from app.core.dependencies import ServiceFactory, create_test_dependencies
from app.database import Base
from app.main import app


class TestConfig(RhizProtocolSettings):
    """Test-specific configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(
            app_env="test",
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/15",  # Test Redis DB
            debug=True,
            **kwargs
        )


class DatabaseTestMixin:
    """Mixin for database testing utilities"""
    
    @pytest.fixture
    async def db_engine(self):
        """Create test database engine"""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        
        # Cleanup
        await engine.dispose()
    
    @pytest.fixture
    async def db_session(self, db_engine):
        """Create test database session"""
        async_session = sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            yield session
    
    @pytest.fixture
    async def db_transaction(self, db_session):
        """Create database transaction (auto-rollback)"""
        transaction = await db_session.begin()
        yield db_session
        await transaction.rollback()


class MockServiceMixin:
    """Mixin for service mocking utilities"""
    
    @pytest.fixture
    def mock_trust_engine(self):
        """Mock trust engine"""
        mock = AsyncMock()
        mock.calculate_trust_score.return_value = 0.85
        mock.update_trust_metrics.return_value = MagicMock()
        return mock
    
    @pytest.fixture
    def mock_pathfinder(self):
        """Mock pathfinder"""
        mock = AsyncMock()
        mock.find_path.return_value = {
            "from_entity": "did:plc:alice",
            "to_entity": "did:plc:bob",
            "hops": [],
            "total_strength": 0.75,
            "distance": 2
        }
        return mock
    
    @pytest.fixture
    def mock_semantic_search(self):
        """Mock semantic search"""
        mock = AsyncMock()
        mock.find_similar_relationships.return_value = []
        mock.generate_embedding.return_value = [0.1] * 384
        return mock
    
    @pytest.fixture
    def mock_signature_verification(self):
        """Mock signature verification"""
        mock = MagicMock()
        mock.verify_relationship_signatures.return_value = {
            "valid": True,
            "signature_count": 2,
            "verified_signatures": 2
        }
        return mock
    
    @pytest.fixture
    def mock_cache_service(self):
        """Mock cache service"""
        mock = AsyncMock()
        mock.get_cached_path.return_value = None
        mock.cache_path_result.return_value = None
        return mock


class APITestMixin:
    """Mixin for API testing utilities"""
    
    @pytest.fixture
    def test_client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_headers(self):
        """Get authenticated request headers"""
        return {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
    
    def assert_api_response(
        self, 
        response, 
        expected_status: int = 200,
        expected_keys: Optional[List[str]] = None
    ):
        """Assert API response format"""
        assert response.status_code == expected_status
        
        if expected_keys:
            data = response.json()
            for key in expected_keys:
                assert key in data
    
    def assert_error_response(
        self, 
        response, 
        expected_status: int,
        expected_error_code: Optional[str] = None
    ):
        """Assert error response format"""
        assert response.status_code == expected_status
        
        data = response.json()
        assert "error" in data
        assert "message" in data
        
        if expected_error_code:
            assert data["error"] == expected_error_code


class DataFixtureMixin:
    """Mixin for test data fixtures"""
    
    @pytest.fixture
    def sample_entity_data(self):
        """Sample entity data"""
        return {
            "id": "did:plc:alice123",
            "displayName": "Alice Chen",
            "entityType": "person",
            "verified": True,
            "bio": "Software engineer and protocol designer"
        }
    
    @pytest.fixture
    def sample_relationship_data(self):
        """Sample relationship data"""
        return {
            "participants": ["did:plc:alice123", "did:plc:bob456"],
            "type": "professional",
            "strength": 85,
            "context": "Co-founded TechCorp together",
            "verification": {
                "consensusScore": 92,
                "attestationCount": 5,
                "verifyCount": 4,
                "disputeCount": 1,
                "lastUpdated": "2025-10-22T12:00:00Z"
            },
            "privacy": {
                "visibility": "public",
                "consent": "full"
            },
            "temporal": {
                "start": "2020-01-15T00:00:00Z",
                "lastInteraction": "2025-10-20T14:30:00Z"
            }
        }
    
    @pytest.fixture
    def sample_trust_metrics(self):
        """Sample trust metrics"""
        return {
            "entity_id": "did:plc:alice123",
            "trustScore": 88,
            "reputation": 91,
            "reciprocity": 85,
            "consistency": 89,
            "relationshipCount": 47,
            "verifiedRelationshipCount": 42
        }


class PerformanceTestMixin:
    """Mixin for performance testing utilities"""
    
    def benchmark_function(self, func, *args, **kwargs):
        """Benchmark function execution time"""
        import time
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        return {
            "result": result,
            "duration": end_time - start_time,
            "function": func.__name__
        }
    
    async def benchmark_async_function(self, func, *args, **kwargs):
        """Benchmark async function execution time"""
        import time
        
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        return {
            "result": result,
            "duration": end_time - start_time,
            "function": func.__name__
        }
    
    def assert_performance_threshold(self, duration: float, threshold: float):
        """Assert performance meets threshold"""
        assert duration <= threshold, f"Function took {duration}s, expected <= {threshold}s"


class RhizTestCase(
    DatabaseTestMixin,
    MockServiceMixin,
    APITestMixin,
    DataFixtureMixin,
    PerformanceTestMixin
):
    """
    Base test case combining all testing utilities
    
    Provides a comprehensive foundation for Rhiz Protocol tests
    """
    
    @pytest.fixture(autouse=True)
    async def setup_test_environment(self):
        """Setup test environment before each test"""
        # Initialize test config
        self.config = TestConfig()
        
        # Setup service factory with test dependencies
        self.service_factory = ServiceFactory(config=self.config)
        
        # Setup mock dependencies
        self.mocks = create_test_dependencies()
        
        yield
        
        # Cleanup after test
        await self._cleanup_test_environment()
    
    async def _cleanup_test_environment(self):
        """Cleanup test environment"""
        # Reset mocks
        for mock in self.mocks.values():
            if hasattr(mock, 'reset_mock'):
                mock.reset_mock()


# Specialized test cases for different components

class TrustEngineTestCase(RhizTestCase):
    """Specialized test case for trust engine testing"""
    
    @pytest.fixture
    async def trust_engine(self, db_session):
        """Create trust engine for testing"""
        return self.service_factory.create_trust_engine(db=db_session)
    
    def assert_trust_score_valid(self, score: float):
        """Assert trust score is valid"""
        assert 0.0 <= score <= 1.0, f"Trust score {score} not in valid range [0.0, 1.0]"
    
    def assert_trust_metrics_complete(self, metrics: Dict[str, Any]):
        """Assert trust metrics are complete"""
        required_fields = [
            "trustScore", "reputation", "reciprocity", 
            "consistency", "relationshipCount", "verifiedRelationshipCount"
        ]
        
        for field in required_fields:
            assert field in metrics, f"Missing required field: {field}"
            assert isinstance(metrics[field], (int, float)), f"Field {field} must be numeric"


class PathfindingTestCase(RhizTestCase):
    """Specialized test case for pathfinding testing"""
    
    @pytest.fixture
    async def pathfinder(self, db_session):
        """Create pathfinder for testing"""
        return self.service_factory.create_pathfinder(db=db_session)
    
    def assert_path_valid(self, path: Dict[str, Any]):
        """Assert path structure is valid"""
        required_fields = ["from_entity", "to_entity", "hops", "total_strength", "distance"]
        
        for field in required_fields:
            assert field in path, f"Missing required field: {field}"
        
        assert isinstance(path["hops"], list), "Hops must be a list"
        assert isinstance(path["distance"], int), "Distance must be an integer"
        assert 0.0 <= path["total_strength"] <= 1.0, "Total strength must be in [0.0, 1.0]"


class APIIntegrationTestCase(RhizTestCase):
    """Specialized test case for API integration testing"""
    
    @pytest.fixture(autouse=True)
    async def setup_api_test(self):
        """Setup API integration test environment"""
        # Override app dependencies with test dependencies
        from app.core.dependencies import get_trust_engine, get_pathfinder
        
        app.dependency_overrides[get_trust_engine] = lambda: self.mocks["trust_engine"]
        app.dependency_overrides[get_pathfinder] = lambda: self.mocks["pathfinder"]
        
        yield
        
        # Clean up overrides
        app.dependency_overrides.clear()
    
    def test_endpoint_with_authentication(self, endpoint: str, method: str = "GET", **kwargs):
        """Test endpoint with authentication"""
        client = TestClient(app)
        headers = self.authenticated_headers()
        
        response = getattr(client, method.lower())(endpoint, headers=headers, **kwargs)
        return response


# Utility functions for test data generation

def generate_test_did(prefix: str = "test") -> str:
    """Generate test DID"""
    import uuid
    return f"did:plc:{prefix}_{uuid.uuid4().hex[:8]}"


def generate_test_relationship(
    entity_a: Optional[str] = None,
    entity_b: Optional[str] = None,
    **overrides
) -> Dict[str, Any]:
    """Generate test relationship data"""
    base_data = {
        "participants": [
            entity_a or generate_test_did("alice"),
            entity_b or generate_test_did("bob")
        ],
        "type": "professional",
        "strength": 75,
        "context": "Test relationship",
        "verification": {
            "consensusScore": 80,
            "attestationCount": 3,
            "verifyCount": 2,
            "disputeCount": 1,
            "lastUpdated": "2025-10-22T12:00:00Z"
        }
    }
    
    base_data.update(overrides)
    return base_data


def generate_test_graph(node_count: int = 10, edge_density: float = 0.3) -> List[Dict[str, Any]]:
    """Generate test graph with specified properties"""
    import random
    
    # Generate nodes
    nodes = [generate_test_did(f"node{i}") for i in range(node_count)]
    
    # Generate edges
    relationships = []
    for i in range(node_count):
        for j in range(i + 1, node_count):
            if random.random() < edge_density:
                rel = generate_test_relationship(
                    entity_a=nodes[i],
                    entity_b=nodes[j],
                    strength=random.randint(50, 100)
                )
                relationships.append(rel)
    
    return relationships


# Test configuration helpers

def override_test_config(**overrides) -> TestConfig:
    """Create test config with overrides"""
    return TestConfig(**overrides)


def create_isolated_test_db() -> str:
    """Create isolated test database URL"""
    import tempfile
    import uuid
    
    temp_dir = tempfile.gettempdir()
    db_name = f"test_rhiz_{uuid.uuid4().hex[:8]}.db"
    return f"sqlite+aiosqlite:///{temp_dir}/{db_name}"


# Assertion helpers

def assert_did_format(did: str):
    """Assert DID format is valid"""
    assert did.startswith(("did:plc:", "did:web:")), f"Invalid DID format: {did}"
    assert len(did) > 10, f"DID too short: {did}"


def assert_at_uri_format(uri: str):
    """Assert AT URI format is valid"""
    assert uri.startswith("at://"), f"Invalid AT URI format: {uri}"
    assert len(uri.split("/")) >= 4, f"AT URI missing components: {uri}"


def assert_timestamp_format(timestamp: str):
    """Assert timestamp format is valid ISO 8601"""
    from datetime import datetime
    
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        pytest.fail(f"Invalid timestamp format: {timestamp}")


# Performance testing utilities

class PerformanceBenchmark:
    """Performance benchmark utility"""
    
    def __init__(self):
        self.results = []
    
    def benchmark(self, name: str, threshold: Optional[float] = None):
        """Decorator for benchmarking functions"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                import time
                
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                duration = end_time - start_time
                
                benchmark_result = {
                    "name": name,
                    "duration": duration,
                    "threshold": threshold,
                    "passed": threshold is None or duration <= threshold
                }
                
                self.results.append(benchmark_result)
                
                if threshold and duration > threshold:
                    pytest.fail(f"{name} took {duration:.3f}s, expected <= {threshold:.3f}s")
                
                return result
            
            return wrapper
        return decorator
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get benchmark results"""
        return self.results.copy()
    
    def clear_results(self):
        """Clear benchmark results"""
        self.results.clear()