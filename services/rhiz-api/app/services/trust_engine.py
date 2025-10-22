"""
Trust scoring engine
Calculates and updates trust metrics for entities using advanced algorithms:
- Temporal decay for relationship freshness
- Network-aware trust propagation (TidalTrust)
- Differential privacy for aggregated metrics
"""

import math
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_service import BaseService
from app.core.exceptions import (
    TrustCalculationError, 
    entity_not_found,
    DatabaseError
)
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.trust_metrics import TrustMetrics


class TrustEngine(BaseService[TrustMetrics]):
    """
    Advanced trust scoring engine with network propagation and temporal dynamics
    
    Implements:
    - TidalTrust algorithm for network-aware trust propagation
    - Temporal decay for relationship freshness
    - Differential privacy for aggregated metrics
    - Comprehensive error handling and logging
    """

    def __init__(
        self, 
        db: AsyncSession, 
        enable_privacy: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(db, logger)
        self.enable_privacy = enable_privacy
        self._entity_cache: Dict[str, Dict] = {}
    
    @property
    def service_name(self) -> str:
        return "trust_engine"

    async def calculate_trust_score(self, entity_id: str, max_depth: int = 3) -> float:
        """
        Calculate composite trust score using network-aware propagation
        
        Args:
            entity_id: Target entity DID
            max_depth: Maximum network depth for trust propagation
            
        Returns:
            Trust score (0.0-1.0) with temporal decay and network effects
            
        Raises:
            TrustCalculationError: If calculation fails
            ValidationError: If entity_id is invalid
        """
        try:
            self.logger.info(f"Calculating trust score for entity {entity_id}")
            
            # Validate entity exists
            await self._validate_entity_exists(entity_id)
            
            start_time = datetime.utcnow()
            
            # Get direct metrics
            direct_metrics = await self._calculate_direct_metrics(entity_id)
            
            # Calculate network-propagated trust (TidalTrust algorithm)
            network_trust = await self._calculate_network_trust(entity_id, max_depth)
            
            # Weighted combination with network effect
            weights = {
                "direct": 0.7,      # Direct relationship metrics
                "network": 0.3,     # Network propagation effect
            }
            
            trust_score = (
                weights["direct"] * direct_metrics["composite"]
                + weights["network"] * network_trust
            )
            
            # Apply differential privacy if enabled
            if self.enable_privacy:
                trust_score = self._add_differential_privacy(trust_score)
            
            # Record metrics
            self._record_operation_metric("calculate_trust_score", start_time)
            
            result = min(1.0, max(0.0, trust_score))
            self.logger.info(f"Trust score for {entity_id}: {result:.3f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Trust calculation failed for {entity_id}: {e}")
            raise TrustCalculationError(
                message=f"Failed to calculate trust score: {str(e)}",
                entity_id=entity_id,
                details={"max_depth": max_depth, "privacy_enabled": self.enable_privacy}
            )

    def _apply_temporal_decay(self, strength: float, last_interaction: datetime) -> float:
        """Apply temporal decay to relationship strength based on recency"""
        if not last_interaction:
            return strength * 0.5  # Default decay for unknown interaction time
            
        days_since = (datetime.utcnow() - last_interaction).days
        
        # Exponential decay with 1-year half-life
        decay_factor = math.exp(-days_since / 365.25)
        
        # Apply decay but maintain minimum of 10% original strength
        return max(0.1 * strength, strength * decay_factor)

    async def _calculate_network_trust(self, entity_id: str, max_depth: int) -> float:
        """
        Implement TidalTrust algorithm for network-aware trust propagation
        
        Propagates trust through the network with diminishing returns,
        considering both path strength and path diversity.
        """
        if max_depth <= 0:
            return 0.0
            
        # Build network graph for entity
        network = await self._build_trust_network(entity_id, max_depth)
        
        if not network:
            return 0.0
            
        # Calculate trust propagation using modified TidalTrust
        total_trust = 0.0
        total_weight = 0.0
        
        for neighbor_id, relationship_data in network.get(entity_id, {}).items():
            # Get direct trust to neighbor
            direct_trust = relationship_data['trust_score']
            edge_weight = relationship_data['weight']
            
            # Recursively calculate neighbor's network trust
            if max_depth > 1:
                neighbor_network_trust = await self._calculate_network_trust(
                    neighbor_id, max_depth - 1
                )
                # Combine direct and network trust with diminishing returns
                propagated_trust = direct_trust * (0.7 + 0.3 * neighbor_network_trust)
            else:
                propagated_trust = direct_trust
                
            total_trust += propagated_trust * edge_weight
            total_weight += edge_weight
            
        return total_trust / total_weight if total_weight > 0 else 0.0

    async def _build_trust_network(
        self, 
        entity_id: str, 
        max_depth: int
    ) -> Dict[str, Dict[str, Dict]]:
        """Build trust network graph around entity"""
        network = {}
        visited = set()
        
        async def build_recursive(current_id: str, depth: int):
            if depth <= 0 or current_id in visited:
                return
                
            visited.add(current_id)
            
            # Get relationships for current entity
            query = select(Relationship).where(
                or_(
                    Relationship.entity_a_id == current_id,
                    Relationship.entity_b_id == current_id
                ),
                Relationship.strength >= 30  # Only consider meaningful relationships
            )
            
            result = await self.db.execute(query)
            relationships = result.scalars().all()
            
            if current_id not in network:
                network[current_id] = {}
                
            for rel in relationships:
                neighbor_id = (
                    rel.entity_b_id if rel.entity_a_id == current_id 
                    else rel.entity_a_id
                )
                
                # Apply temporal decay to relationship strength
                decayed_strength = self._apply_temporal_decay(
                    rel.strength / 100.0,  # Convert to 0-1 scale
                    rel.last_interaction
                )
                
                # Calculate relationship weight (considers verification)
                verification_boost = min(0.2, rel.verifier_count / 50)
                trust_score = min(1.0, decayed_strength + verification_boost)
                
                network[current_id][neighbor_id] = {
                    'trust_score': trust_score,
                    'weight': rel.consensus_score,
                    'relationship_id': rel.id
                }
                
                # Recursively build for neighbors
                if depth > 1:
                    await build_recursive(neighbor_id, depth - 1)
        
        await build_recursive(entity_id, max_depth)
        return network

    def _add_differential_privacy(self, score: float, epsilon: float = 1.0) -> float:
        """Add Laplace noise for differential privacy"""
        sensitivity = 0.1  # Maximum change in score from single relationship
        noise = np.random.laplace(0, sensitivity / epsilon)
        return max(0.0, min(1.0, score + noise))

    async def _calculate_direct_metrics(self, entity_id: str) -> dict:
        """Calculate individual trust metrics with temporal awareness"""
        reputation = await self._calculate_reputation(entity_id)
        reciprocity = await self._calculate_reciprocity(entity_id)
        consistency = await self._calculate_consistency(entity_id)
        verification_ratio = await self._calculate_verification_ratio(entity_id)
        
        # Enhanced weighting that considers relationship freshness
        weights = {
            "reputation": 0.35,
            "reciprocity": 0.25,
            "consistency": 0.25,
            "verification_ratio": 0.15,
        }
        
        composite = (
            weights["reputation"] * reputation
            + weights["reciprocity"] * reciprocity
            + weights["consistency"] * consistency
            + weights["verification_ratio"] * verification_ratio
        )

        return {
            "reputation": reputation,
            "reciprocity": reciprocity,
            "consistency": consistency,
            "verification_ratio": verification_ratio,
            "composite": composite,
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
        """Update or create trust metrics for an entity using advanced algorithms"""
        # Calculate metrics with network propagation
        trust_score = await self.calculate_trust_score(entity_id)
        metrics = await self._calculate_direct_metrics(entity_id)

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
    
    async def _validate_entity_exists(self, entity_id: str) -> None:
        """Validate that entity exists in the system"""
        try:
            # Check if entity exists (simplified check)
            query = select(Relationship).where(
                or_(
                    Relationship.entity_a_id == entity_id,
                    Relationship.entity_b_id == entity_id
                )
            ).limit(1)
            
            result = await self.db.execute(query)
            if not result.first():
                # Entity has no relationships, might not exist
                # In production, would check entities table
                self.logger.warning(f"Entity {entity_id} has no relationships")
            
        except Exception as e:
            self.logger.error(f"Entity validation failed for {entity_id}: {e}")
            raise entity_not_found("entity", entity_id)
    
    # Implement abstract methods from BaseService
    async def _perform_create(self, create_data) -> TrustMetrics:
        """Not implemented - trust metrics are calculated, not created directly"""
        raise NotImplementedError("Trust metrics are calculated, not created directly")
    
    async def _perform_get_by_id(self, entity_id: str) -> Optional[TrustMetrics]:
        """Get trust metrics by entity ID"""
        query = select(TrustMetrics).where(TrustMetrics.entity_id == entity_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _perform_update(self, entity_id: str, update_data) -> Optional[TrustMetrics]:
        """Update trust metrics (recalculate)"""
        return await self.update_trust_metrics(entity_id)
    
    async def _perform_delete(self, entity_id: str) -> bool:
        """Delete trust metrics for entity"""
        query = select(TrustMetrics).where(TrustMetrics.entity_id == entity_id)
        result = await self.db.execute(query)
        metrics = result.scalar_one_or_none()
        
        if metrics:
            await self.db.delete(metrics)
            await self.db.flush()
            return True
        return False
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> TrustMetrics:
        """Convert dictionary to TrustMetrics entity"""
        # Simplified conversion - in production would use proper ORM mapping
        metrics = TrustMetrics()
        for key, value in data.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        return metrics

