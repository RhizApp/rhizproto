"""
Attestation event processor

Handles attestation creation and conviction recalculation
"""

import logging
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cache_service import get_unified_cache
from app.services.conviction import ConvictionCalculator

from ..types import EventType, ProtocolEvent
from .base import EventProcessor

logger = logging.getLogger(__name__)


class AttestationEventProcessor(EventProcessor):
    """Process attestation events from firehose"""

    def __init__(self, db: AsyncSession):
        """
        Initialize processor

        Args:
            db: Database session
        """
        self.db = db
        self.conviction_calc = ConvictionCalculator()

    def can_process(self, event: ProtocolEvent) -> bool:
        """Check if this is an attestation event"""
        return event.event_type == EventType.ATTESTATION_CREATED

    async def process(self, event: ProtocolEvent) -> bool:
        """
        Process attestation event

        Args:
            event: Attestation event

        Returns:
            True if successful
        """
        try:
            payload = event.payload

            # Insert attestation into database
            insert_query = text(
                """
                INSERT INTO attestations (
                    uri, cid, attester_did, target_uri, attestation_type,
                    confidence, evidence, suggested_strength, created_at, indexed_at
                ) VALUES (
                    :uri, :cid, :attester_did, :target_uri, :attestation_type,
                    :confidence, :evidence, :suggested_strength, :created_at, :indexed_at
                )
                ON CONFLICT (uri) DO UPDATE SET
                    attestation_type = EXCLUDED.attestation_type,
                    confidence = EXCLUDED.confidence,
                    evidence = EXCLUDED.evidence,
                    indexed_at = EXCLUDED.indexed_at
            """
            )

            await self.db.execute(insert_query, payload)
            await self.db.commit()

            event.add_stage_result("database_write", True)

            # Recalculate conviction for target
            target_uri = payload["target_uri"]
            await self._recalculate_conviction(target_uri, event)

            event.add_stage_result("conviction_recalculation", True)

            logger.info(f"Attestation processed: {payload['uri']}")
            return True

        except Exception as e:
            logger.error(f"Attestation processing failed: {e}")
            event.add_stage_result("attestation_processing", False, str(e))
            raise

    async def _recalculate_conviction(self, target_uri: str, event: ProtocolEvent):
        """Recalculate conviction score for target"""
        from app.services.conviction import Attestation

        # Get all attestations for target
        attestations_query = text(
            """
            SELECT uri, attester_did, attestation_type, confidence, created_at
            FROM attestations
            WHERE target_uri = :target_uri
        """
        )

        attestation_rows = await self.db.execute(
            attestations_query, {"target_uri": target_uri}
        )
        attestations = attestation_rows.fetchall()

        # Convert to Attestation objects
        attestation_list = [
            Attestation(
                uri=row.uri,
                attester_did=row.attester_did,
                attestation_type=row.attestation_type,
                confidence=row.confidence,
                created_at=row.created_at,
            )
            for row in attestations
        ]

        # Calculate conviction
        conviction = self.conviction_calc.calculate_conviction(target_uri, attestation_list, self.db)

        # Update conviction_scores cache table
        cache_query = text(
            """
            INSERT INTO conviction_scores (
                target_uri, score, attestation_count,
                verify_count, dispute_count, strengthen_count, weaken_count,
                last_updated, trend, top_attester_reputation
            ) VALUES (
                :target_uri, :score, :attestation_count,
                :verify_count, :dispute_count, :strengthen_count, :weaken_count,
                :last_updated, :trend, :top_attester_reputation
            )
            ON CONFLICT (target_uri) DO UPDATE SET
                score = EXCLUDED.score,
                attestation_count = EXCLUDED.attestation_count,
                verify_count = EXCLUDED.verify_count,
                dispute_count = EXCLUDED.dispute_count,
                strengthen_count = EXCLUDED.strengthen_count,
                weaken_count = EXCLUDED.weaken_count,
                last_updated = EXCLUDED.last_updated,
                trend = EXCLUDED.trend,
                top_attester_reputation = EXCLUDED.top_attester_reputation
        """
        )

        await self.db.execute(
            cache_query,
            {
                "target_uri": target_uri,
                "score": conviction["score"],
                "attestation_count": conviction["attestation_count"],
                "verify_count": conviction["verify_count"],
                "dispute_count": conviction["dispute_count"],
                "strengthen_count": conviction["strengthen_count"],
                "weaken_count": conviction["weaken_count"],
                "last_updated": datetime.utcnow(),
                "trend": conviction["trend"],
                "top_attester_reputation": conviction["top_attester_reputation"],
            },
        )
        await self.db.commit()

        # Invalidate cache
        cache = get_unified_cache()
        await cache.delete(f"conviction:{target_uri}")

        logger.info(f"Conviction recalculated for {target_uri}: {conviction['score']}/100")

