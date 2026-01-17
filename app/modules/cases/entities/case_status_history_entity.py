"""
Case Status History entity - Domain model.
"""

import uuid
from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base


class CaseStatusHistory(Base):
    """
    Audit log for tracking case status transitions.
    Ensures accountability and traceability.
    """

    __tablename__ = "case_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False,
    )

    old_status: Mapped[str] = mapped_column(String(50), nullable=False)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)

    changed_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    changed_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    # Relationships
    case = relationship("Case", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="status_changes")
