"""
Trust metrics model - stores calculated trust scores for entities
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TrustMetrics(Base):
    """Trust metrics model"""

    __tablename__ = "trust_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("entities.id"), unique=True, nullable=False, index=True
    )

    # Core trust metrics (0.0-1.0)
    trust_score: Mapped[float] = mapped_column(Float, nullable=False)
    reputation: Mapped[float] = mapped_column(Float, nullable=False)
    reciprocity: Mapped[float] = mapped_column(Float, nullable=False)
    consistency: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationship counts
    relationship_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    verified_relationship_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamps
    last_calculated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    entity: Mapped["Entity"] = relationship("Entity", back_populates="trust_metrics")

    def __repr__(self) -> str:
        return f"<TrustMetrics entity={self.entity_id} score={self.trust_score:.2f}>"

