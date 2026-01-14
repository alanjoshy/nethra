import uuid
from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class Media(Base):
    """
    Represents media evidence (images, videos, CCTV footage)
    associated with a case.
    """

    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    camera_type: Mapped[str | None] = mapped_column(String(100))

    capture_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))
    uploaded_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    case = relationship("Case", back_populates="media_items")
