"""
Person entity definition.
"""

from sqlalchemy import Column, String, Date, ForeignKey, Enum as SqEnum, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.base import Base


class PersonRole(str, enum.Enum):
    SUSPECT = "suspect"
    VICTIM = "victim"
    WITNESS = "witness"


class Person(Base):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    identification_number = Column(String, nullable=True, unique=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    case_links = relationship("CasePerson", back_populates="person", cascade="all, delete-orphan")


class CasePerson(Base):
    __tablename__ = "case_persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    role = Column(SqEnum(PersonRole), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    case = relationship("Case", backref="person_links")
    person = relationship("Person", back_populates="case_links")
