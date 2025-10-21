"""
Graph Indexer Service
Indexes relationship records from AT Protocol repos into PostgreSQL for fast graph queries
"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity
from app.models.relationship import Relationship


class IndexedRelationship:
    """Indexed relationship data from firehose"""

    def __init__(
        self,
        uri: str,
        cid: str,
        did: str,
        participants: Tuple[str, str],
        relationship_type: str,
        strength: float,
        context: str,
        created_at: datetime,
    ):
        self.uri = uri
        self.cid = cid
        self.did = did
        self.participants = participants
        self.relationship_type = relationship_type
        self.strength = strength
        self.context = context
        self.created_at = created_at


class GraphIndexer:
    """
    Indexes relationship records into PostgreSQL
    Source of truth is AT Protocol repos, database is for fast queries
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def index_relationship(self, indexed: IndexedRelationship) -> None:
        """
        Index a relationship record from the firehose

        Args:
            indexed: Indexed relationship data
        """
        # Check if participants exist as entities
        await self._ensure_entities_exist(indexed.participants)

        # Check if relationship already exists
        existing = await self._get_relationship_by_uri(indexed.uri)

        if existing:
            # Update existing relationship
            existing.at_uri = indexed.uri
            existing.cid = indexed.cid
            existing.type = indexed.relationship_type
            existing.strength = indexed.strength
            existing.context = indexed.context
            existing.updated_at = datetime.utcnow()
        else:
            # Create new relationship
            relationship = Relationship(
                at_uri=indexed.uri,
                cid=indexed.cid,
                participant_did_1=indexed.participants[0],
                participant_did_2=indexed.participants[1],
                type=indexed.relationship_type,
                strength=indexed.strength,
                context=indexed.context,
                created_at=indexed.created_at,
                updated_at=datetime.utcnow(),
            )
            self.session.add(relationship)

        await self.session.commit()

    async def remove_relationship(self, uri: str) -> None:
        """
        Remove a relationship from the index

        Args:
            uri: AT URI of the relationship record
        """
        relationship = await self._get_relationship_by_uri(uri)
        if relationship:
            await self.session.delete(relationship)
            await self.session.commit()

    async def index_profile(
        self,
        uri: str,
        cid: str,
        did: str,
        display_name: str,
        entity_type: str,
        bio: Optional[str] = None,
    ) -> None:
        """
        Index an entity profile

        Args:
            uri: AT URI of the profile record
            cid: Content ID
            did: Entity DID
            display_name: Display name
            entity_type: Type of entity (person, organization, agent)
            bio: Optional biography
        """
        # Check if entity exists
        result = await self.session.execute(select(Entity).where(Entity.did == did))
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing entity
            existing.profile_uri = uri
            existing.profile_cid = cid
            existing.name = display_name
            existing.type = entity_type
            existing.bio = bio
            existing.updated_at = datetime.utcnow()
        else:
            # Create new entity
            entity = Entity(
                did=did,
                profile_uri=uri,
                profile_cid=cid,
                name=display_name,
                type=entity_type,
                bio=bio,
                verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.session.add(entity)

        await self.session.commit()

    async def get_relationships_for_did(
        self, did: str, limit: int = 100
    ) -> List[Relationship]:
        """
        Get all relationships for a DID

        Args:
            did: Entity DID
            limit: Maximum number of relationships to return

        Returns:
            List of Relationship objects
        """
        result = await self.session.execute(
            select(Relationship)
            .where(
                or_(
                    Relationship.participant_did_1 == did,
                    Relationship.participant_did_2 == did,
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def _ensure_entities_exist(self, dids: Tuple[str, str]) -> None:
        """Ensure both participant DIDs exist as entities"""
        for did in dids:
            result = await self.session.execute(select(Entity).where(Entity.did == did))
            entity = result.scalar_one_or_none()

            if not entity:
                # Create placeholder entity (will be updated when profile is indexed)
                entity = Entity(
                    did=did,
                    name=f"Entity {did[:12]}...",
                    type="person",  # Default
                    verified=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                self.session.add(entity)

        await self.session.commit()

    async def _get_relationship_by_uri(self, uri: str) -> Optional[Relationship]:
        """Get relationship by AT URI"""
        result = await self.session.execute(
            select(Relationship).where(Relationship.at_uri == uri)
        )
        return result.scalar_one_or_none()


async def create_graph_indexer() -> GraphIndexer:
    """Create a graph indexer instance"""
    db = await anext(get_db())
    return GraphIndexer(db)

