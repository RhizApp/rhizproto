"""
Internal API endpoints

Not public-facing. Used by:
- TypeScript firehose indexer to push events to Python pipeline
- Internal monitoring and administration
"""

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from app.infrastructure.events import EventPriority, EventType, ProtocolEvent, get_event_pipeline

router = APIRouter(prefix="/internal", tags=["internal"])


class IngestEventRequest(BaseModel):
    """Request to ingest an event"""

    event_type: str
    payload: Dict[str, Any]
    did: str
    priority: int = 1


@router.post("/events")
async def ingest_event(request: IngestEventRequest, x_internal_key: str = Header(...)):
    """
    Ingest event from TypeScript firehose indexer

    Requires X-Internal-Key header for authentication

    Args:
        request: Event data
        x_internal_key: Internal API key header

    Returns:
        Event ID and enqueue status
    """
    # Validate internal key
    from app.config import get_settings

    settings = get_settings()
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal API key")

    # Create event
    try:
        event = ProtocolEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType(request.event_type),
            payload=request.payload,
            did=request.did,
            priority=EventPriority(request.priority),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid event type or priority: {e}"
        )

    # Enqueue in pipeline
    pipeline = get_event_pipeline()
    success = await pipeline.enqueue(event)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event pipeline backpressure active - queue full",
        )

    return {"status": "enqueued", "event_id": event.event_id}


@router.get("/events/metrics")
async def get_pipeline_metrics(x_internal_key: str = Header(...)):
    """
    Get event pipeline metrics

    Requires X-Internal-Key header for authentication

    Returns:
        Pipeline metrics (throughput, latency, queue size, etc.)
    """
    # Validate internal key
    from app.config import get_settings

    settings = get_settings()
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal API key")

    pipeline = get_event_pipeline()
    metrics = pipeline.get_metrics()

    return {
        "events_processed": metrics.events_processed,
        "events_failed": metrics.events_failed,
        "events_in_queue": metrics.events_in_queue,
        "avg_processing_time_ms": metrics.avg_processing_time_ms,
        "throughput_per_second": metrics.throughput_per_second,
        "worker_utilization": metrics.worker_utilization,
        "backpressure_active": metrics.backpressure_active,
    }


@router.get("/events/dead-letter")
async def get_dead_letter_queue(x_internal_key: str = Header(...)):
    """
    Get dead letter queue (failed events)

    Requires X-Internal-Key header for authentication

    Returns:
        List of events that failed after max retries
    """
    # Validate internal key
    from app.config import get_settings

    settings = get_settings()
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal API key")

    pipeline = get_event_pipeline()
    dead_letters = pipeline.get_dead_letter_queue()

    return {
        "count": len(dead_letters),
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "did": e.did,
                "retry_count": e.retry_count,
                "timestamp": e.timestamp.isoformat(),
                "stages": e.processing_stages,
            }
            for e in dead_letters
        ],
    }

