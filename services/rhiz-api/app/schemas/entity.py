"""
Pydantic schemas for Entity - DID-native
"""

from datetime import datetime

from pydantic import BaseModel, Field


class EntityBase(BaseModel):
    """Base entity schema"""

    type: str
    name: str = Field(..., min_length=1, max_length=255)
    bio: str | None = Field(None, max_length=1000)
    avatar_url: str | None = None
    handle: str | None = None


class EntityCreate(EntityBase):
    """Schema for creating an entity - DID is now required"""

    did: str = Field(..., min_length=1, max_length=255, description="AT Protocol DID")
    profile_uri: str | None = Field(None, description="AT URI of profile record")
    profile_cid: str | None = Field(None, description="Content ID of profile record")


class EntityUpdate(BaseModel):
    """Schema for updating an entity"""

    name: str | None = Field(None, min_length=1, max_length=255)
    bio: str | None = Field(None, max_length=1000)
    avatar_url: str | None = None
    handle: str | None = None
    profile_uri: str | None = None
    profile_cid: str | None = None


class EntityResponse(EntityBase):
    """Schema for entity responses"""

    did: str  # Primary key
    profile_uri: str | None = None
    profile_cid: str | None = None
    verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

