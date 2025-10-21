"""
Entity API endpoints - DID-native
CRUD operations for entities using DIDs as primary keys
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity
from app.schemas.entity import EntityCreate, EntityResponse, EntityUpdate
from app.services.identity_resolver import get_identity_resolver

router = APIRouter()


@router.post("/", response_model=EntityResponse, status_code=201)
async def create_entity(
    entity: EntityCreate,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """
    Create a new entity with DID as primary key

    The DID must be a valid AT Protocol DID (did:plc:* or did:web:*)
    Optionally includes profile_uri and profile_cid if profile record exists in AT Protocol repo
    """
    # Check if entity already exists
    existing_query = select(Entity).where(Entity.did == entity.did)
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Entity with DID {entity.did} already exists")

    # Optionally validate DID (can be commented out for performance)
    # resolver = get_identity_resolver()
    # is_valid = await resolver.validate(entity.did)
    # if not is_valid:
    #     raise HTTPException(status_code=400, detail="Invalid DID")

    # Create entity
    db_entity = Entity(
        did=entity.did,
        profile_uri=entity.profile_uri,
        profile_cid=entity.profile_cid,
        type=entity.type,
        name=entity.name,
        bio=entity.bio,
        avatar_url=entity.avatar_url,
        handle=entity.handle,
        verified=False,
    )

    db.add(db_entity)
    await db.commit()
    await db.refresh(db_entity)

    return EntityResponse.model_validate(db_entity)


@router.get("/{did:path}", response_model=EntityResponse)
async def get_entity(
    did: str,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """
    Get an entity by DID

    DID format: did:plc:abc123... or did:web:example.com
    """
    query = select(Entity).where(Entity.did == did)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity with DID {did} not found")

    return EntityResponse.model_validate(entity)


@router.get("/by-handle/{handle}", response_model=EntityResponse)
async def get_entity_by_handle(
    handle: str,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """
    Get an entity by handle

    Handle format: alice.bsky.social
    This first resolves the handle to a DID, then returns the entity
    """
    # Try database first
    query = select(Entity).where(Entity.handle == handle)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if entity:
        return EntityResponse.model_validate(entity)

    # If not in database, try resolving via AT Protocol
    try:
        resolver = get_identity_resolver()
        identity = await resolver.resolve(handle)

        # Try again with resolved DID
        query = select(Entity).where(Entity.did == identity.did)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()

        if entity:
            return EntityResponse.model_validate(entity)
    except Exception:
        pass

    raise HTTPException(status_code=404, detail=f"Entity with handle {handle} not found")


@router.patch("/{did:path}", response_model=EntityResponse)
async def update_entity(
    did: str,
    updates: EntityUpdate,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """Update an entity by DID"""
    query = select(Entity).where(Entity.did == did)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity with DID {did} not found")

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)

    await db.commit()
    await db.refresh(entity)

    return EntityResponse.model_validate(entity)


@router.delete("/{did:path}", status_code=204)
async def delete_entity(
    did: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an entity by DID"""
    query = select(Entity).where(Entity.did == did)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity with DID {did} not found")

    await db.delete(entity)
    await db.commit()

