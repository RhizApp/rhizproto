"""
Entity model - represents a person, organization, or agent
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EntityType(str, PyEnum):
    """Entity types"""

    PERSON = "person"
    ORGANIZATION = "organization"
    AGENT = "agent"


class Entity(Base):
    """Entity model"""

    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False)
    did: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    handle: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    trust_metrics: Mapped["TrustMetrics"] = relationship(
        "TrustMetrics", back_populates="entity", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Entity {self.id} ({self.type}): {self.name}>"

