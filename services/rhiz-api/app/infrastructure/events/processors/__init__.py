"""
Event processors for protocol pipeline
"""

from .base import EventProcessor
from .relationship import RelationshipEventProcessor
from .attestation import AttestationEventProcessor

__all__ = [
    "EventProcessor",
    "RelationshipEventProcessor",
    "AttestationEventProcessor",
]

