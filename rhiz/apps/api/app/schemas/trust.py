"""
Pydantic schemas for Trust Metrics
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TrustMetricsResponse(BaseModel):
    """Schema for trust metrics responses"""

    entity_id: str
    trust_score: float = Field(..., ge=0.0, le=1.0)
    reputation: float = Field(..., ge=0.0, le=1.0)
    reciprocity: float = Field(..., ge=0.0, le=1.0)
    consistency: float = Field(..., ge=0.0, le=1.0)
    relationship_count: int = Field(..., ge=0)
    verified_relationship_count: int = Field(..., ge=0)
    last_calculated: datetime

    model_config = {"from_attributes": True}


class TrustHealthResponse(BaseModel):
    """Schema for trust health analytics"""

    entity_id: str
    trust_level: str  # very_high, high, medium, low, very_low
    trust_score: float
    network_size: int
    verified_ratio: float
    recent_activity: int  # interactions in last 30 days
    recommendations: list[str]

