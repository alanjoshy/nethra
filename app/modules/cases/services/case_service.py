"""
Case service - Business logic for case management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cases.entities.case_entity import Case
from app.modules.cases.entities.case_status_history_entity import CaseStatusHistory
from app.modules.cases.repositories.case_repository import CaseRepository
from app.shared.exceptions import NotFoundError


class CaseService:
    """
    Case service.
    Handles business logic for case operations.
    """
    
    @staticmethod
    async def create_case(
        db: AsyncSession,
        primary_incident_id: UUID,
        title: str,
        status: str,
        notes: Optional[str] = None,
    ) -> Case:
        """Create a new case."""
        case = Case(
            primary_incident_id=primary_incident_id,
            title=title,
            status=status,
            notes=notes,
        )
        return await CaseRepository.create(db, case)
    
    @staticmethod
    async def list_cases(db: AsyncSession) -> list[Case]:
        """Get all cases."""
        return await CaseRepository.get_all(db)
    
    @staticmethod
    async def get_case(db: AsyncSession, case_id: UUID) -> Case:
        """Get a case by ID."""
        case = await CaseRepository.get_by_id(db, case_id)
        if not case:
            raise NotFoundError(resource="Case", identifier=case_id)
        return case
    
    @staticmethod
    async def update_case(
        db: AsyncSession,
        case_id: UUID,
        title: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Case:
        """Update a case."""
        case = await CaseService.get_case(db, case_id)
        
        if title is not None:
            case.title = title
        if notes is not None:
            case.notes = notes
        
        return await CaseRepository.save(db, case)
    
    @staticmethod
    async def update_case_status(
        db: AsyncSession,
        case_id: UUID,
        new_status: str,
        changed_by: UUID,
    ) -> Case:
        """Update case status and record in history."""
        case = await CaseService.get_case(db, case_id)
        
        old_status = case.status
        case.status = new_status
        
        # Create status history record
        history = CaseStatusHistory(
            case_id=case_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_at=datetime.utcnow(),
        )
        await CaseRepository.create_status_history(db, history)
        
        return await CaseRepository.save(db, case)
    
    @staticmethod
    async def delete_case(db: AsyncSession, case_id: UUID) -> None:
        """Delete a case."""
        case = await CaseService.get_case(db, case_id)
        await CaseRepository.delete(db, case)
