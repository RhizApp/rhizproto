"""
Pydantic schemas for Graph operations
"""

from pydantic import BaseModel, Field


class GraphHop(BaseModel):
    """A single hop in a graph path"""

    from_entity: str = Field(..., alias="from")
    to_entity: str = Field(..., alias="to")
    relationship_id: str
    strength: float = Field(..., ge=0.0, le=1.0)

    model_config = {"populate_by_name": True}


class GraphPathResponse(BaseModel):
    """Response schema for graph path finding"""

    from_entity: str = Field(..., alias="from")
    to_entity: str = Field(..., alias="to")
    hops: list[GraphHop]
    total_strength: float = Field(..., ge=0.0, le=1.0)
    distance: int = Field(..., ge=0)

    model_config = {"populate_by_name": True}


class GraphQueryRequest(BaseModel):
    """Request schema for graph queries"""

    from_entity: str = Field(..., alias="from")
    to_entity: str = Field(..., alias="to")
    max_hops: int = Field(default=6, ge=1, le=10)
    min_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    relationship_types: list[str] | None = None
    exclude_entities: list[str] | None = None

    model_config = {"populate_by_name": True}


class NeighborsResponse(BaseModel):
    """Response schema for getting entity neighbors"""

    entity_id: str
    neighbors: list[dict]  # List of {entity_id, relationship_id, strength}
    count: int

