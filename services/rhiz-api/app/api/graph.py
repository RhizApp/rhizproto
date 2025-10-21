"""
Graph API endpoints - DID-native with AT URI references
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
    Find trust-weighted path between two entities using DIDs

    Paths return AT URIs for relationship records, enabling verification
    of the relationships in the AT Protocol repos.

    Query:
    - from_entity: Source DID (did:plc:alice...)
    - to_entity: Target DID (did:plc:bob...)
    - max_hops: Maximum path length (default: 6)
    - min_strength: Minimum relationship strength (default: 0.5)

    Returns:
    - Path with AT URIs for each relationship hop
    - Total strength (weighted product)
    - Distance in hops
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


@router.get("/neighbors/{did:path}", response_model=NeighborsResponse)
async def get_neighbors(
    did: str,
    min_strength: float = 0.0,
    db: AsyncSession = Depends(get_db),
) -> NeighborsResponse:
    """
    Get direct neighbors of an entity by DID

    Returns all entities directly connected via relationships,
    with AT URIs for verifying relationships in AT Protocol repos.

    Parameters:
    - did: Entity DID (did:plc:alice...)
    - min_strength: Minimum relationship strength (default: 0.0)

    Returns:
    - List of neighbor entities with DIDs
    - Relationship AT URIs and strengths
    - Total count
    """
    pathfinder = PathFinder(db)

    neighbors = await pathfinder.get_neighbors(did, min_strength)

    return NeighborsResponse(
        entity_did=did,
        neighbors=neighbors,
        count=len(neighbors),
    )

