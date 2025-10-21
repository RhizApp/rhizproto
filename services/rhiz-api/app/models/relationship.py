"""
Relationship model - represents verified relationships between entities
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RelationshipType(str, PyEnum):
    """Relationship types"""

    PROFESSIONAL = "professional"
    PERSONAL = "personal"
    FAMILY = "family"
    SOCIAL = "social"
    CIVIC = "civic"
    EDUCATIONAL = "educational"


class Visibility(str, PyEnum):
    """Visibility levels"""

    PUBLIC = "public"
    NETWORK = "network"
    PRIVATE = "private"


class ConsentLevel(str, PyEnum):
    """Consent levels"""

    FULL = "full"
    LIMITED = "limited"
    ANONYMOUS = "anonymous"


class Relationship(Base):
    """
    Relationship model - DID-native with AT Protocol content-addressing
    Source of truth: AT Protocol repos
    Database: Fast query index
    """

    __tablename__ = "relationships"

    # AT Protocol record references (source of truth)
    at_uri: Mapped[str] = mapped_column(
        String(500), primary_key=True, index=True
    )  # at://did:plc:alice/net.rhiz.relationship.record/tid
    cid: Mapped[str] = mapped_column(String(255), nullable=False)  # Content ID

    # Participants (DIDs)
    participant_did_1: Mapped[str] = mapped_column(
        String(255), ForeignKey("entities.did"), nullable=False, index=True
    )
    participant_did_2: Mapped[str] = mapped_column(
        String(255), ForeignKey("entities.did"), nullable=False, index=True
    )

    # Relationship data (indexed for fast queries)
    type: Mapped[RelationshipType] = mapped_column(Enum(RelationshipType), nullable=False)
    strength: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0-1.0
    context: Mapped[str] = mapped_column(Text, nullable=False)

    # Verification
    consensus_score: Mapped[float] = mapped_column(Float, nullable=False)
    verifier_count: Mapped[int] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    last_verified: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Privacy
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), nullable=False)
    consent: Mapped[ConsentLevel] = mapped_column(Enum(ConsentLevel), nullable=False)

    # Temporal
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_interaction: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    history: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=list
    )  # Array of strength history points

    # Protocol metadata
    contributors: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list
    )  # Array of DIDs
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_relationships_participants", "participant_did_1", "participant_did_2"),
        Index("ix_relationships_type_strength", "type", "strength"),
        Index("ix_relationships_cid", "cid"),
    )

    def __repr__(self) -> str:
        return f"<Relationship {self.at_uri} ({self.type}): {self.participant_did_1} <-> {self.participant_did_2}>"

