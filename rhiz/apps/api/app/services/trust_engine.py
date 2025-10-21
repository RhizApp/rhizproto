"""
Trust scoring engine
Calculates and updates trust metrics for entities
"""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.trust_metrics import TrustMetrics


class TrustEngine:
    """Trust scoring engine"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_trust_score(self, entity_id: str) -> float:
        """Calculate composite trust score for an entity"""
        metrics = await self._calculate_metrics(entity_id)

        # Weighted combination
        weights = {
            "reputation": 0.3,
            "reciprocity": 0.25,
            "consistency": 0.25,
            "verification_ratio": 0.2,
        }

        trust_score = (
            weights["reputation"] * metrics["reputation"]
            + weights["reciprocity"] * metrics["reciprocity"]
            + weights["consistency"] * metrics["consistency"]
            + weights["verification_ratio"] * metrics["verification_ratio"]
        )

        return min(1.0, max(0.0, trust_score))

    async def _calculate_metrics(self, entity_id: str) -> dict:
        """Calculate individual trust metrics"""
        reputation = await self._calculate_reputation(entity_id)
        reciprocity = await self._calculate_reciprocity(entity_id)
        consistency = await self._calculate_consistency(entity_id)
        verification_ratio = await self._calculate_verification_ratio(entity_id)

        return {
            "reputation": reputation,
            "reciprocity": reciprocity,
            "consistency": consistency,
            "verification_ratio": verification_ratio,
        }

    async def _calculate_reputation(self, entity_id: str) -> float:
        """Calculate reputation based on network position"""
        # Get all relationships
        query = select(Relationship).where(
            (Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id)
        )
        result = await self.db.execute(query)
        relationships = result.scalars().all()

        if not relationships:
            return 0.5  # Default neutral reputation

        # Average strength of relationships
        avg_strength = sum(r.strength for r in relationships) / len(relationships)

        # Boost for high verifier counts
        avg_verifiers = sum(r.verifier_count for r in relationships) / len(relationships)
        verifier_boost = min(0.2, avg_verifiers / 50)  # Max 0.2 boost

        return min(1.0, avg_strength + verifier_boost)

    async def _calculate_reciprocity(self, entity_id: str) -> float:
        """Calculate reciprocity score"""
        # For simplicity, use relationship strength as proxy
        # In production, track interaction patterns
        query = select(func.avg(Relationship.strength)).where(
            (Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id)
        )
        result = await self.db.execute(query)
        avg_strength = result.scalar()

        return float(avg_strength) if avg_strength else 0.5

    async def _calculate_consistency(self, entity_id: str) -> float:
        """Calculate consistency based on interaction patterns"""
        # Get relationships with recent interactions
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        query = select(Relationship).where(
            ((Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id))
            & (Relationship.last_interaction >= thirty_days_ago)
        )
        result = await self.db.execute(query)
        recent_relationships = result.scalars().all()

        # Get total relationships
        total_query = select(func.count(Relationship.id)).where(
            (Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id)
        )
        total_result = await self.db.execute(total_query)
        total_count = total_result.scalar() or 0

        if total_count == 0:
            return 0.5

        # Consistency = ratio of recently active relationships
        consistency = len(recent_relationships) / total_count
        return min(1.0, consistency * 1.5)  # Boost to account for expected activity levels

    async def _calculate_verification_ratio(self, entity_id: str) -> float:
        """Calculate ratio of verified relationships"""
        # Get all relationships
        query = select(Relationship).where(
            (Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id)
        )
        result = await self.db.execute(query)
        relationships = result.scalars().all()

        if not relationships:
            return 0.0

        # Count verified (consensus_score >= 0.7)
        verified = sum(1 for r in relationships if r.consensus_score >= 0.7)

        return verified / len(relationships)

    async def update_trust_metrics(self, entity_id: str) -> TrustMetrics:
        """Update or create trust metrics for an entity"""
        # Calculate metrics
        trust_score = await self.calculate_trust_score(entity_id)
        metrics = await self._calculate_metrics(entity_id)

        # Get relationship counts
        count_query = select(func.count(Relationship.id)).where(
            (Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id)
        )
        count_result = await self.db.execute(count_query)
        relationship_count = count_result.scalar() or 0

        verified_query = select(func.count(Relationship.id)).where(
            ((Relationship.entity_a_id == entity_id) | (Relationship.entity_b_id == entity_id))
            & (Relationship.consensus_score >= 0.7)
        )
        verified_result = await self.db.execute(verified_query)
        verified_count = verified_result.scalar() or 0

        # Check if metrics exist
        existing_query = select(TrustMetrics).where(TrustMetrics.entity_id == entity_id)
        existing_result = await self.db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.trust_score = trust_score
            existing.reputation = metrics["reputation"]
            existing.reciprocity = metrics["reciprocity"]
            existing.consistency = metrics["consistency"]
            existing.relationship_count = relationship_count
            existing.verified_relationship_count = verified_count
            existing.last_calculated = datetime.utcnow()
            await self.db.flush()
            return existing
        else:
            # Create new
            new_metrics = TrustMetrics(
                entity_id=entity_id,
                trust_score=trust_score,
                reputation=metrics["reputation"],
                reciprocity=metrics["reciprocity"],
                consistency=metrics["consistency"],
                relationship_count=relationship_count,
                verified_relationship_count=verified_count,
                last_calculated=datetime.utcnow(),
            )
            self.db.add(new_metrics)
            await self.db.flush()
            return new_metrics

