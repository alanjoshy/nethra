"""
Case repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cases.entities.case_entity import Case


class CaseRepository:
    """
    Repository for Case entity.
    Handles all database operations for cases.
    """
    
    async def get_case_by_id(
        self,
        db: AsyncSession,
        case_id: UUID
    ) -> Optional[Case]:
        """
        Get a case by ID.
        
        Args:
            db: Database session
            case_id: Case UUID
        
        Returns:
            Case object if found, None otherwise
        """
        result = await db.execute(
            select(Case).where(Case.id == case_id)
        )
        return result.scalar_one_or_none()
