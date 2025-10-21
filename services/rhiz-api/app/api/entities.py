"""
Entity API endpoints
CRUD operations for entities
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity
from app.schemas.entity import EntityCreate, EntityResponse, EntityUpdate

router = APIRouter()


@router.post("/", response_model=EntityResponse, status_code=201)
async def create_entity(
    entity: EntityCreate,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """Create a new entity"""
    # Check if entity already exists
    existing_query = select(Entity).where(Entity.id == entity.id)
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Entity already exists")

    # Create entity
    db_entity = Entity(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        bio=entity.bio,
        avatar_url=entity.avatar_url,
        did=entity.did,
        handle=entity.handle,
        verified=False,
    )

    db.add(db_entity)
    await db.commit()
    await db.refresh(db_entity)

    return EntityResponse.model_validate(db_entity)


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """Get an entity by ID"""
    query = select(Entity).where(Entity.id == entity_id)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return EntityResponse.model_validate(entity)


@router.patch("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    updates: EntityUpdate,
    db: AsyncSession = Depends(get_db),
) -> EntityResponse:
    """Update an entity"""
    query = select(Entity).where(Entity.id == entity_id)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)

    await db.commit()
    await db.refresh(entity)

    return EntityResponse.model_validate(entity)


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an entity"""
    query = select(Entity).where(Entity.id == entity_id)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    await db.delete(entity)
    await db.commit()

