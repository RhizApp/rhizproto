"""
Pydantic schemas for Entity
"""

from datetime import datetime

from pydantic import BaseModel, Field


class EntityBase(BaseModel):
    """Base entity schema"""

    type: str
    name: str = Field(..., min_length=1, max_length=255)
    bio: str | None = Field(None, max_length=1000)
    avatar_url: str | None = None
    did: str | None = None
    handle: str | None = None


class EntityCreate(EntityBase):
    """Schema for creating an entity"""

    id: str = Field(..., min_length=1, max_length=255)


class EntityUpdate(BaseModel):
    """Schema for updating an entity"""

    name: str | None = Field(None, min_length=1, max_length=255)
    bio: str | None = Field(None, max_length=1000)
    avatar_url: str | None = None
    handle: str | None = None


class EntityResponse(EntityBase):
    """Schema for entity responses"""

    id: str
    verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

