"""
Case repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cases.entities.case_entity import Case
from app.modules.cases.entities.case_status_history_entity import CaseStatusHistory


class CaseRepository:
    """
    Repository for Case entity.
    Handles all database operations for cases.
    """
    
    @staticmethod
    async def create(
        db: AsyncSession,
        case: Case
    ) -> Case:
        """Create a new case."""
        db.add(case)
        await db.commit()
        await db.refresh(case)
        return case
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        case_id: UUID
    ) -> Optional[Case]:
        """Get a case by ID."""
        result = await db.execute(
            select(Case).where(Case.id == case_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Case]:
        """Get all cases."""
        result = await db.execute(select(Case))
        return list(result.scalars().all())
    
    @staticmethod
    async def save(db: AsyncSession, case: Case) -> Case:
        """Update an existing case."""
        await db.commit()
        await db.refresh(case)
        return case
    
    @staticmethod
    async def delete(db: AsyncSession, case: Case) -> None:
        """Delete a case."""
        await db.delete(case)
        await db.commit()
    
    @staticmethod
    async def create_status_history(
        db: AsyncSession,
        history: CaseStatusHistory
    ) -> CaseStatusHistory:
        """Create a status history record."""
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history
