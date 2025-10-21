"""
Analytics API endpoints
Trust health and network statistics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity
from app.models.trust_metrics import TrustMetrics
from app.schemas.trust import TrustHealthResponse, TrustMetricsResponse
from app.services.trust_engine import TrustEngine

router = APIRouter()


@router.get("/trust-health/{entity_id}", response_model=TrustHealthResponse)
async def get_trust_health(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
) -> TrustHealthResponse:
    """
    Get trust health metrics for an entity

    Provides a comprehensive view of an entity's trust status
    with actionable recommendations.
    """
    # Check entity exists
    entity_query = select(Entity).where(Entity.id == entity_id)
    entity_result = await db.execute(entity_query)
    entity = entity_result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get or calculate trust metrics
    trust_engine = TrustEngine(db)
    metrics = await trust_engine.update_trust_metrics(entity_id)

    # Determine trust level
    score = metrics.trust_score
    if score >= 0.9:
        level = "very_high"
    elif score >= 0.75:
        level = "high"
    elif score >= 0.5:
        level = "medium"
    elif score >= 0.25:
        level = "low"
    else:
        level = "very_low"

    # Generate recommendations
    recommendations = []
    if metrics.verified_relationship_count < 5:
        recommendations.append("Verify more relationships to increase trust")
    if metrics.relationship_count < 10:
        recommendations.append("Expand your network by adding more connections")
    if metrics.consistency < 0.6:
        recommendations.append("Increase interaction frequency with your network")
    if metrics.reciprocity < 0.7:
        recommendations.append("Focus on building mutual relationships")

    return TrustHealthResponse(
        entity_id=entity_id,
        trust_level=level,
        trust_score=score,
        network_size=metrics.relationship_count,
        verified_ratio=(
            metrics.verified_relationship_count / metrics.relationship_count
            if metrics.relationship_count > 0
            else 0.0
        ),
        recent_activity=0,  # TODO: Calculate from temporal data
        recommendations=recommendations,
    )


@router.get("/trust-metrics/{entity_id}", response_model=TrustMetricsResponse)
async def get_trust_metrics(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
) -> TrustMetricsResponse:
    """Get detailed trust metrics for an entity"""
    query = select(TrustMetrics).where(TrustMetrics.entity_id == entity_id)
    result = await db.execute(query)
    metrics = result.scalar_one_or_none()

    if not metrics:
        # Calculate if not exists
        trust_engine = TrustEngine(db)
        metrics = await trust_engine.update_trust_metrics(entity_id)
        await db.commit()

    return TrustMetricsResponse.model_validate(metrics)


@router.get("/network-stats")
async def get_network_stats(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get overall network statistics

    Provides aggregate metrics about the entire relationship graph.
    """
    # Count entities
    entity_count_query = select(func.count(Entity.id))
    entity_count_result = await db.execute(entity_count_query)
    entity_count = entity_count_result.scalar()

    # Count relationships (simplified - would need Relationship model)
    # For now, return basic stats
    return {
        "total_entities": entity_count or 0,
        "total_relationships": 0,  # TODO: Add when relationship count is available
        "avg_trust_score": 0.0,  # TODO: Calculate from TrustMetrics
        "verified_entities": 0,  # TODO: Count verified entities
    }

