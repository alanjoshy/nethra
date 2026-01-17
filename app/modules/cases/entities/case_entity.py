"""
Case entity - Domain model.
"""

import uuid
from sqlalchemy import String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base


class Case(Base):
    """
    Represents an investigation case.
    A case is anchored by one primary incident.
    """

    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    primary_incident_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        unique=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    notes: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    primary_incident = relationship("Incident", back_populates="case")
    media_items = relationship("Media", back_populates="case")
    status_history = relationship("CaseStatusHistory", back_populates="case")
