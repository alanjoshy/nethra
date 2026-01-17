"""
Incident entity - Domain model.
"""

import uuid
from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

from app.core.base import Base



class Incident(Base):
    """
    Represents a reported incident.
    Each incident is anchored to exactly one case.
    """

    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    reported_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    incident_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    occurred_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    # PostGIS geography point (longitude, latitude)
    location: Mapped[str] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    notes: Mapped[str | None] = mapped_column(Text) 

    # Relationships
    reported_by_user = relationship("User", back_populates="reported_incidents")
    case = relationship("Case", back_populates="primary_incident", uselist=False)
