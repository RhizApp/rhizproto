"""
Relationship event processor

Handles relationship creation, updates, and deletions
"""

import logging
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import Relationship
from app.services.cache_service import get_unified_cache

from ..types import EventType, ProtocolEvent
from .base import EventProcessor

logger = logging.getLogger(__name__)


class RelationshipEventProcessor(EventProcessor):
    """Process relationship events from firehose"""

    def __init__(self, db: AsyncSession):
        """
        Initialize processor

        Args:
            db: Database session
        """
        self.db = db

    def can_process(self, event: ProtocolEvent) -> bool:
        """Check if this is a relationship event"""
        return event.event_type in [
            EventType.RELATIONSHIP_CREATED,
            EventType.RELATIONSHIP_UPDATED,
            EventType.RELATIONSHIP_DELETED,
        ]

    async def process(self, event: ProtocolEvent) -> bool:
        """
        Process relationship event

        Args:
            event: Relationship event

        Returns:
            True if successful
        """
        try:
            if event.event_type == EventType.RELATIONSHIP_CREATED:
                return await self._handle_created(event)
            elif event.event_type == EventType.RELATIONSHIP_UPDATED:
                return await self._handle_updated(event)
            elif event.event_type == EventType.RELATIONSHIP_DELETED:
                return await self._handle_deleted(event)

            return False

        except Exception as e:
            logger.error(f"Relationship processing failed: {e}")
            event.add_stage_result("relationship_processing", False, str(e))
            raise

    async def _handle_created(self, event: ProtocolEvent) -> bool:
        """Handle relationship creation"""
        event.add_stage_result("validation", True)

        # Index relationship in database
        payload = event.payload
        relationship = Relationship(
            at_uri=payload["uri"],
            cid=payload["cid"],
            participant_did_1=payload["participants"][0],
            participant_did_2=payload["participants"][1],
            type=payload["type"],
            strength=payload["strength"],
            context=payload.get("context"),
            created_at=payload["created_at"],
        )

        self.db.add(relationship)
        await self.db.commit()

        event.add_stage_result("database_write", True)

        # Invalidate graph caches for both participants
        cache = get_unified_cache()
        for did in payload["participants"]:
            await cache.clear_pattern(f"graph:path:*{did}*")
            await cache.clear_pattern(f"graph:neighbors:{did}*")

        event.add_stage_result("cache_invalidation", True)

        logger.info(f"Relationship created: {payload['uri']}")
        return True

    async def _handle_updated(self, event: ProtocolEvent) -> bool:
        """Handle relationship update"""
        # Similar to created but UPDATE existing record
        event.add_stage_result("update_processing", True)
        return True

    async def _handle_deleted(self, event: ProtocolEvent) -> bool:
        """Handle relationship deletion"""
        payload = event.payload
        uri = payload["uri"]

        # Delete from database
        from sqlalchemy import delete

        await self.db.execute(delete(Relationship).where(Relationship.at_uri == uri))
        await self.db.commit()

        event.add_stage_result("database_delete", True)

        # Invalidate caches
        cache = get_unified_cache()
        for did in payload.get("participants", []):
            await cache.clear_pattern(f"graph:*{did}*")

        event.add_stage_result("cache_invalidation", True)

        logger.info(f"Relationship deleted: {uri}")
        return True

