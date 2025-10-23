"""
Tests for enhanced health check API

Tests liveness, readiness, and detailed health endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_liveness(self):
        """Test GET /health (liveness)"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @patch("app.api.health.get_unified_cache")
    @patch("app.api.health.get_event_pipeline")
    def test_readiness_all_healthy(self, mock_pipeline, mock_cache):
        """Test GET /health/ready when all systems healthy"""
        # Mock cache health
        mock_cache_instance = MagicMock()
        mock_cache_instance.health_check = AsyncMock(
            return_value={"status": "healthy", "hit_rate": 0.75}
        )
        mock_cache.return_value = mock_cache_instance

        # Mock pipeline metrics
        mock_pipeline_instance = MagicMock()
        mock_metrics = MagicMock()
        mock_metrics.backpressure_active = False
        mock_metrics.events_in_queue = 100
        mock_pipeline_instance.get_metrics.return_value = mock_metrics
        mock_pipeline.return_value = mock_pipeline_instance

        # Call endpoint
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["checks"]["cache"] == "healthy"
        assert data["checks"]["event_pipeline"] == "healthy"

    @patch("app.api.health.get_unified_cache")
    @patch("app.api.health.get_event_pipeline")
    def test_readiness_degraded(self, mock_pipeline, mock_cache):
        """Test GET /health/ready when system degraded"""
        # Mock cache healthy
        mock_cache_instance = MagicMock()
        mock_cache_instance.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_cache.return_value = mock_cache_instance

        # Mock pipeline with backpressure
        mock_pipeline_instance = MagicMock()
        mock_metrics = MagicMock()
        mock_metrics.backpressure_active = True  # Degraded
        mock_metrics.events_in_queue = 9000
        mock_pipeline_instance.get_metrics.return_value = mock_metrics
        mock_pipeline.return_value = mock_pipeline_instance

        # Call endpoint
        response = client.get("/health/ready")

        assert response.status_code == 503  # Service unavailable
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["event_pipeline"] == "degraded"

    @patch("app.api.health.get_unified_cache")
    @patch("app.api.health.get_event_pipeline")
    def test_detailed_health(self, mock_pipeline, mock_cache):
        """Test GET /health/detailed"""
        # Mock cache with stats
        mock_cache_instance = MagicMock()
        mock_cache_instance.health_check = AsyncMock(
            return_value={"status": "healthy", "hit_rate": 0.85}
        )

        mock_stats = MagicMock()
        mock_stats.hit_rate = 0.85
        mock_stats.total_keys = 1000
        mock_stats.hits = 8500
        mock_stats.misses = 1500
        mock_stats.memory_usage_bytes = 1024 * 1024 * 50  # 50 MB

        mock_cache_instance.get_stats = AsyncMock(return_value=mock_stats)
        mock_cache.return_value = mock_cache_instance

        # Mock pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.is_running.return_value = True

        mock_metrics = MagicMock()
        mock_metrics.events_processed = 1000
        mock_metrics.events_failed = 10
        mock_metrics.events_in_queue = 50
        mock_metrics.avg_processing_time_ms = 25.5
        mock_metrics.throughput_per_second = 100.0
        mock_metrics.worker_utilization = 0.5
        mock_metrics.backpressure_active = False

        mock_pipeline_instance.get_metrics.return_value = mock_metrics
        mock_pipeline_instance.get_dead_letter_queue.return_value = []
        mock_pipeline.return_value = mock_pipeline_instance

        # Call endpoint
        response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "version" in data
        assert "dependencies" in data
        assert data["dependencies"]["cache"]["status"] == "healthy"
        assert data["dependencies"]["event_pipeline"]["status"] == "healthy"
        assert data["dependencies"]["cache"]["stats"]["hit_rate"] == 0.85


class TestInternalAPI:
    """Tests for internal event ingestion API"""

    @patch("app.api.internal.get_event_pipeline")
    def test_ingest_event(self, mock_get_pipeline):
        """Test POST /internal/events"""
        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.enqueue = AsyncMock(return_value=True)
        mock_get_pipeline.return_value = mock_pipeline

        # Call endpoint with valid key
        response = client.post(
            "/internal/events",
            json={
                "event_type": "relationship.created",
                "payload": {"test": "data"},
                "did": "did:plc:alice",
                "priority": 1,
            },
            headers={"X-Internal-Key": "dev-internal-key-change-in-prod"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enqueued"
        assert "event_id" in data

    def test_ingest_event_invalid_key(self):
        """Test ingestion with invalid API key"""
        response = client.post(
            "/internal/events",
            json={
                "event_type": "relationship.created",
                "payload": {},
                "did": "did:plc:alice",
            },
            headers={"X-Internal-Key": "invalid-key"},
        )

        assert response.status_code == 403

    @patch("app.api.internal.get_event_pipeline")
    def test_ingest_event_backpressure(self, mock_get_pipeline):
        """Test ingestion when backpressure active"""
        # Mock pipeline rejecting events
        mock_pipeline = MagicMock()
        mock_pipeline.enqueue = AsyncMock(return_value=False)  # Backpressure
        mock_get_pipeline.return_value = mock_pipeline

        response = client.post(
            "/internal/events",
            json={
                "event_type": "relationship.created",
                "payload": {},
                "did": "did:plc:alice",
            },
            headers={"X-Internal-Key": "dev-internal-key-change-in-prod"},
        )

        assert response.status_code == 503  # Service unavailable

    @patch("app.api.internal.get_event_pipeline")
    def test_get_pipeline_metrics(self, mock_get_pipeline):
        """Test GET /internal/events/metrics"""
        # Mock pipeline metrics
        mock_pipeline = MagicMock()
        mock_metrics = MagicMock()
        mock_metrics.events_processed = 1000
        mock_metrics.events_failed = 5
        mock_metrics.events_in_queue = 50
        mock_metrics.avg_processing_time_ms = 25.0
        mock_metrics.throughput_per_second = 100.0
        mock_metrics.worker_utilization = 0.5
        mock_metrics.backpressure_active = False

        mock_pipeline.get_metrics.return_value = mock_metrics
        mock_get_pipeline.return_value = mock_pipeline

        response = client.get(
            "/internal/events/metrics", headers={"X-Internal-Key": "dev-internal-key-change-in-prod"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["events_processed"] == 1000
        assert data["throughput_per_second"] == 100.0

