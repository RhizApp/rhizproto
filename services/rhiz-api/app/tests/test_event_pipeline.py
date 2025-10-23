"""
Tests for real-time event pipeline

Tests event processing, worker pool, retry logic, and backpressure
"""

import pytest
import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.infrastructure.events.pipeline import EventPipeline
from app.infrastructure.events.types import ProtocolEvent, EventType, EventPriority
from app.infrastructure.events.processors import EventProcessor


class MockProcessor(EventProcessor):
    """Mock processor for testing"""

    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.processed_events = []

    def can_process(self, event: ProtocolEvent) -> bool:
        return event.event_type == EventType.RELATIONSHIP_CREATED

    async def process(self, event: ProtocolEvent) -> bool:
        self.processed_events.append(event)

        if not self.should_succeed:
            raise Exception("Processing failed")

        await asyncio.sleep(0.01)  # Simulate work
        return True


class TestEventPipeline:
    """Tests for event pipeline"""

    @pytest.mark.asyncio
    async def test_pipeline_startup_shutdown(self):
        """Test pipeline starts and stops cleanly"""
        pipeline = EventPipeline(max_queue_size=100, num_workers=2)

        assert not pipeline.is_running()

        await pipeline.start()
        assert pipeline.is_running()

        await pipeline.stop()
        assert not pipeline.is_running()

    @pytest.mark.asyncio
    async def test_enqueue_and_process_event(self):
        """Test enqueueing and processing events"""
        pipeline = EventPipeline(max_queue_size=100, num_workers=2)
        processor = MockProcessor(should_succeed=True)
        pipeline.register_processor(processor)

        await pipeline.start()

        # Create and enqueue event
        event = ProtocolEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.RELATIONSHIP_CREATED,
            payload={"test": "data"},
            did="did:plc:test",
            priority=EventPriority.NORMAL,
        )

        success = await pipeline.enqueue(event)
        assert success is True

        # Wait for processing
        await asyncio.sleep(0.5)

        # Check event was processed
        assert len(processor.processed_events) == 1
        assert processor.processed_events[0].event_id == event.event_id

        # Check metrics
        metrics = pipeline.get_metrics()
        assert metrics.events_processed == 1

        await pipeline.stop()

    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        """Test events processed in priority order"""
        pipeline = EventPipeline(max_queue_size=100, num_workers=1)
        processor = MockProcessor()
        pipeline.register_processor(processor)

        await pipeline.start()

        # Enqueue events with different priorities
        low_event = ProtocolEvent(
            event_id="low",
            event_type=EventType.RELATIONSHIP_CREATED,
            payload={},
            did="did:plc:test",
            priority=EventPriority.LOW,
        )

        critical_event = ProtocolEvent(
            event_id="critical",
            event_type=EventType.RELATIONSHIP_CREATED,
            payload={},
            did="did:plc:test",
            priority=EventPriority.CRITICAL,
        )

        # Enqueue low first, then critical
        await pipeline.enqueue(low_event)
        await pipeline.enqueue(critical_event)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Critical should be processed first
        assert len(processor.processed_events) == 2
        assert processor.processed_events[0].event_id == "critical"
        assert processor.processed_events[1].event_id == "low"

        await pipeline.stop()

    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test retry with exponential backoff"""
        pipeline = EventPipeline(max_queue_size=100, num_workers=1)
        processor = MockProcessor(should_succeed=False)  # Will fail
        pipeline.register_processor(processor)

        await pipeline.start()

        event = ProtocolEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.RELATIONSHIP_CREATED,
            payload={},
            did="did:plc:test",
            priority=EventPriority.NORMAL,
        )

        await pipeline.enqueue(event)

        # Wait for retries
        await asyncio.sleep(5.0)

        # Should have attempted 4 times (original + 3 retries)
        assert len(processor.processed_events) == 4

        # Should be in dead letter queue
        dead_letters = pipeline.get_dead_letter_queue()
        assert len(dead_letters) > 0

        await pipeline.stop()

    @pytest.mark.asyncio
    async def test_backpressure(self):
        """Test backpressure when queue too full"""
        pipeline = EventPipeline(max_queue_size=10, num_workers=1, backpressure_threshold=0.8)

        # Don't start pipeline to keep events in queue

        # Enqueue up to backpressure threshold (80% of 10 = 8)
        for i in range(8):
            event = ProtocolEvent(
                event_id=str(i),
                event_type=EventType.RELATIONSHIP_CREATED,
                payload={},
                did="did:plc:test",
                priority=EventPriority.NORMAL,
            )
            success = await pipeline.enqueue(event)
            assert success is True

        # Next event should trigger backpressure
        event = ProtocolEvent(
            event_id="should_reject",
            event_type=EventType.RELATIONSHIP_CREATED,
            payload={},
            did="did:plc:test",
            priority=EventPriority.NORMAL,
        )

        success = await pipeline.enqueue(event)
        assert success is False

        # Metrics should show backpressure active
        metrics = pipeline.get_metrics()
        assert metrics.backpressure_active is True

    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test metrics are tracked correctly"""
        pipeline = EventPipeline(max_queue_size=100, num_workers=2)
        processor = MockProcessor(should_succeed=True)
        pipeline.register_processor(processor)

        await pipeline.start()

        # Process some events
        for i in range(5):
            event = ProtocolEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.RELATIONSHIP_CREATED,
                payload={},
                did="did:plc:test",
                priority=EventPriority.NORMAL,
            )
            await pipeline.enqueue(event)

        # Wait for processing
        await asyncio.sleep(1.0)

        metrics = pipeline.get_metrics()

        assert metrics.events_processed == 5
        assert metrics.events_failed == 0
        assert metrics.avg_processing_time_ms > 0
        assert metrics.throughput_per_second >= 0

        await pipeline.stop()


class TestCacheService:
    """Tests for unified cache service"""

    @pytest.mark.asyncio
    async def test_memory_backend(self):
        """Test with memory backend"""
        cache = CacheService(backend="memory")

        await cache.set("test", "value", ttl=60)
        value = await cache.get("test")

        assert value == "value"

        stats = await cache.get_stats()
        assert stats.total_keys == 1

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
    async def test_fallback_on_error(self):
        """Test fallback to memory when Redis fails"""
        # Invalid Redis URL should trigger fallback
        cache = CacheService(backend="redis", redis_url="redis://invalid:9999", fallback_to_memory=True)

        # Should still work via fallback
        await cache.set("test", "value")
        value = await cache.get("test")

        assert value == "value"
        await cache.close()

