"""Conviction API endpoints

Provides XRPC endpoints for querying conviction scores and attestations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.conviction import ConvictionCalculator, Attestation as ConvictionAttestation

router = APIRouter(prefix="/xrpc/net.rhiz.conviction", tags=["conviction"])


@router.get("/getScore")
async def get_conviction_score(
    uri: str = Query(..., description="AT URI of attested record"),
    db: Session = Depends(get_db)
):
    """
    Get conviction score for any attested record.
    
    Returns cached score if available, calculates fresh if not.
    
    Example:
        GET /xrpc/net.rhiz.conviction.getScore?uri=at://did:plc:alice/net.rhiz.relationship.record/abc123
    """
    # Check if cached
    cached_query = text("""
        SELECT target_uri, score, attestation_count, verify_count, 
               dispute_count, strengthen_count, weaken_count,
               last_updated, trend, top_attester_reputation
        FROM conviction_scores 
        WHERE target_uri = :uri
    """)
    
    cached = db.execute(cached_query, {"uri": uri}).first()
    
    if cached:
        return {
            "uri": uri,
            "conviction": {
                "score": cached.score,
                "attestationCount": cached.attestation_count,
                "verifyCount": cached.verify_count,
                "disputeCount": cached.dispute_count,
                "strengthenCount": cached.strengthen_count,
                "weakenCount": cached.weaken_count,
                "lastUpdated": cached.last_updated.isoformat(),
                "trend": cached.trend,
                "topAttesterReputation": cached.top_attester_reputation
            }
        }
    
    # Calculate fresh if not cached
    attestations_query = text("""
        SELECT uri, attester_did, attestation_type, confidence, created_at
        FROM attestations 
        WHERE target_uri = :uri
    """)
    
    attestation_rows = db.execute(attestations_query, {"uri": uri}).fetchall()
    
    if not attestation_rows:
        raise HTTPException(
            status_code=404, 
            detail=f"No attestations found for URI: {uri}"
        )
    
    # Convert to Attestation objects
    attestations = [
        ConvictionAttestation(
            uri=row.uri,
            attester_did=row.attester_did,
            attestation_type=row.attestation_type,
            confidence=row.confidence,
            created_at=row.created_at
        )
        for row in attestation_rows
    ]
    
    # Calculate conviction
    calc = ConvictionCalculator()
    conviction = calc.calculate_conviction(uri, attestations, db)
    
    # Cache the result
    cache_query = text("""
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
    """)
    
    db.execute(cache_query, {
        "target_uri": uri,
        "score": conviction['score'],
        "attestation_count": conviction['attestation_count'],
        "verify_count": conviction['verify_count'],
        "dispute_count": conviction['dispute_count'],
        "strengthen_count": conviction['strengthen_count'],
        "weaken_count": conviction['weaken_count'],
        "last_updated": datetime.utcnow(),
        "trend": conviction['trend'],
        "top_attester_reputation": conviction['top_attester_reputation']
    })
    db.commit()
    
    return {
        "uri": uri,
        "conviction": {
            "score": conviction['score'],
            "attestationCount": conviction['attestation_count'],
            "verifyCount": conviction['verify_count'],
            "disputeCount": conviction['dispute_count'],
            "strengthenCount": conviction['strengthen_count'],
            "weakenCount": conviction['weaken_count'],
            "lastUpdated": datetime.utcnow().isoformat(),
            "trend": conviction['trend'],
            "topAttesterReputation": conviction['top_attester_reputation']
        }
    }


@router.get("/listAttestations")
async def list_attestations(
    uri: str = Query(..., description="AT URI of attested record"),
    type: Optional[str] = Query(None, description="Filter by attestation type (verify|dispute|strengthen|weaken)"),
    minConfidence: Optional[int] = Query(None, description="Minimum confidence level (0-100)"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    cursor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all attestations for a record with pagination.
    
    Example:
        GET /xrpc/net.rhiz.conviction.listAttestations?uri=at://...&type=verify&limit=20
    """
    
    # Build query
    query_parts = ["SELECT * FROM attestations WHERE target_uri = :uri"]
    params = {"uri": uri}
    
    if type:
        query_parts.append("AND attestation_type = :type")
        params["type"] = type
    
    if minConfidence:
        query_parts.append("AND confidence >= :min_confidence")
        params["min_confidence"] = minConfidence
    
    query_parts.append("ORDER BY created_at DESC")
    
    if cursor:
        query_parts.append("AND created_at < :cursor")
        params["cursor"] = cursor
    
    query_parts.append("LIMIT :limit")
    params["limit"] = limit + 1  # Fetch one extra to check if more exist
    
    query = text(" ".join(query_parts))
    attestation_rows = db.execute(query, params).fetchall()
    
    # Check if more results exist
    has_more = len(attestation_rows) > limit
    if has_more:
        attestation_rows = attestation_rows[:limit]
        next_cursor = attestation_rows[-1].created_at.isoformat()
    else:
        next_cursor = None
    
    # Fetch attester profiles
    result = []
    for row in attestation_rows:
        # Get attester entity
        attester_query = text("""
            SELECT did, name, type 
            FROM entities 
            WHERE did = :did
        """)
        attester_row = db.execute(attester_query, {"did": row.attester_did}).first()
        
        # Get attester trust score for reputation
        trust_query = text("""
            SELECT trust_score 
            FROM entities 
            WHERE did = :did
        """)
        trust_row = db.execute(trust_query, {"did": row.attester_did}).first()
        
        result.append({
            "uri": row.uri,
            "cid": row.cid,
            "record": {
                "targetRelationship": row.target_uri,
                "attester": row.attester_did,
                "attestationType": row.attestation_type,
                "confidence": row.confidence,
                "evidence": row.evidence,
                "createdAt": row.created_at.isoformat()
            },
            "attester": {
                "did": attester_row.did,
                "name": attester_row.name,
                "type": attester_row.type
            } if attester_row else None,
            "attesterReputation": trust_row.trust_score if trust_row else 0
        })
    
    return {
        "attestations": result,
        "cursor": next_cursor
    }

