import uuid
from sqlalchemy import String, TIMESTAMP, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base




class User(Base):
    """User entity."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed password (bcrypt)",
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="admin | officer | analyst",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    # Relationships 
    reported_incidents = relationship(
        "app.modules.incidents.entities.incident_entity.Incident",
        back_populates="reported_by_user",
    )

    status_changes = relationship(
        "app.modules.cases.entities.case_status_history_entity.CaseStatusHistory",
        back_populates="changed_by_user",
    )
