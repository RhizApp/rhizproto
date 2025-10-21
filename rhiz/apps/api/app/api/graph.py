"""
Graph API endpoints
Path finding and network analysis
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.graph import GraphPathResponse, GraphQueryRequest, NeighborsResponse
from app.services.pathfinder import PathFinder

router = APIRouter()


@router.post("/find-path", response_model=GraphPathResponse)
async def find_path(
    query: GraphQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> GraphPathResponse:
    """
    Find trust-weighted path between two entities

    This endpoint uses BFS to find the shortest path with configurable
    constraints on hop count and relationship strength.
    """
    pathfinder = PathFinder(db)

    path = await pathfinder.find_path(
        from_entity=query.from_entity,
        to_entity=query.to_entity,
        max_hops=query.max_hops,
        min_strength=query.min_strength,
        relationship_types=query.relationship_types,
        exclude_entities=query.exclude_entities,
    )

    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"No path found between {query.from_entity} and {query.to_entity}",
        )

    return path


@router.get("/neighbors/{entity_id}", response_model=NeighborsResponse)
async def get_neighbors(
    entity_id: str,
    min_strength: float = 0.0,
    db: AsyncSession = Depends(get_db),
) -> NeighborsResponse:
    """
    Get direct neighbors of an entity

    Returns all entities directly connected to the given entity,
    optionally filtered by minimum relationship strength.
    """
    pathfinder = PathFinder(db)

    neighbors = await pathfinder.get_neighbors(entity_id, min_strength)

    return NeighborsResponse(
        entity_id=entity_id,
        neighbors=neighbors,
        count=len(neighbors),
    )

