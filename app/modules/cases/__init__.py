"""
Cases Module - Public API

This is the ONLY file that other modules should import from.
All internal implementation details are hidden.
"""

from app.modules.cases.entities.case_entity import Case
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.cases.services.case_service import CaseService

__all__ = [
    "Case",
    "CaseRepository",
    "CaseService",
]
