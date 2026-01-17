"""
Case service - Business logic for case management.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cases.entities.case_entity import Case
from app.modules.cases.repositories.case_repository import CaseRepository
from app.shared.exceptions import NotFoundError


class CaseService:
    """
    Case service.
    Handles business logic for case operations.
    """
    
    def __init__(self, case_repository: CaseRepository):
        self._case_repository = case_repository
    
    async def get_case_by_id(
        self,
        db: AsyncSession,
        case_id: UUID
    ) -> Case:
        """
        Get a case by ID.
        
        Args:
            db: Database session
            case_id: Case UUID
        
        Returns:
            Case object
        
        Raises:
            NotFoundError: If case not found
        """
        case = await self._case_repository.get_case_by_id(db, case_id)
        if not case:
            raise NotFoundError(resource="Case", identifier=case_id)
        return case
