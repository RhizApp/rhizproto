"""
Event types and dataclasses for protocol event pipeline
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    """Protocol event types"""

    RELATIONSHIP_CREATED = "relationship.created"
    RELATIONSHIP_UPDATED = "relationship.updated"
    RELATIONSHIP_DELETED = "relationship.deleted"
    ATTESTATION_CREATED = "attestation.created"
    ENTITY_PROFILE_UPDATED = "entity.profile.updated"
    TRUST_SCORE_INVALIDATED = "trust.invalidated"


class EventPriority(Enum):
    """Event priority levels"""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ProtocolEvent:
    """
    Event in the protocol pipeline

    Represents a change in the protocol state (relationship, attestation, entity, etc.)
    """

    event_id: str
    event_type: EventType
    payload: Dict[str, Any]
    did: str  # DID that triggered the event
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    processing_stages: List[Dict[str, Any]] = field(default_factory=list)

    def add_stage_result(self, stage: str, success: bool, error: Optional[str] = None):
        """
        Add processing stage result

        Args:
            stage: Stage name
            success: Whether stage succeeded
            error: Error message if failed
        """
        self.processing_stages.append(
            {
                "stage": stage,
                "timestamp": datetime.utcnow().isoformat(),
                "success": success,
                "error": error,
            }
        )


@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""

    events_processed: int = 0
    events_failed: int = 0
    events_in_queue: int = 0
    avg_processing_time_ms: float = 0.0
    throughput_per_second: float = 0.0
    worker_utilization: float = 0.0
    backpressure_active: bool = False

