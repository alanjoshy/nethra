"""
Person schemas.
"""

from app.modules.persons.schemas.person_schemas import (
    PersonCreateRequest,
    PersonUpdateRequest,
    PersonResponse,
    CasePersonLinkRequest,
    CasePersonResponse,
)

__all__ = [
    "PersonCreateRequest",
    "PersonUpdateRequest",
    "PersonResponse",
    "CasePersonLinkRequest",
    "CasePersonResponse",
]
