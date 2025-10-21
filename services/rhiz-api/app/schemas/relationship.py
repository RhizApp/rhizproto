"""
Pydantic schemas for Relationship
"""

from datetime import datetime

from pydantic import BaseModel, Field


class RelationshipBase(BaseModel):
    """Base relationship schema"""

    type: str
    strength: float = Field(..., ge=0.0, le=1.0)
    context: str = Field(..., min_length=1, max_length=500)
    visibility: str
    consent: str


class RelationshipCreate(RelationshipBase):
    """Schema for creating a relationship"""

    entity_a_id: str
    entity_b_id: str


class RelationshipResponse(RelationshipBase):
    """Schema for relationship responses"""

    id: str
    entity_a_id: str
    entity_b_id: str
    consensus_score: float
    verifier_count: int
    confidence: float
    last_verified: datetime
    start_date: datetime
    last_interaction: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

