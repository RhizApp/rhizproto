"""
Real-time event processing infrastructure

Provides event pipeline for processing AT Protocol firehose events
"""

from .types import EventType, EventPriority, ProtocolEvent, PipelineMetrics
from .pipeline import EventPipeline

__all__ = [
    "EventType",
    "EventPriority",
    "ProtocolEvent",
    "PipelineMetrics",
    "EventPipeline",
]


# Singleton instance
_event_pipeline: EventPipeline | None = None


def get_event_pipeline() -> EventPipeline:
    """Get singleton event pipeline instance"""
    global _event_pipeline
    if _event_pipeline is None:
        from app.config import get_settings

        settings = get_settings()
        _event_pipeline = EventPipeline(
            max_queue_size=10000, num_workers=10, backpressure_threshold=0.8
        )

    return _event_pipeline


async def close_event_pipeline():
    """Close event pipeline"""
    global _event_pipeline
    if _event_pipeline:
        await _event_pipeline.stop()
        _event_pipeline = None

