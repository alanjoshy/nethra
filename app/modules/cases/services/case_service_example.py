"""
Example: How Cases module communicates with Users module.

This demonstrates the inter-module communication pattern.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cases.entities.case_entity import Case
from app.modules.cases.repositories.case_repository import CaseRepository
from app.shared.exceptions import NotFoundError
from app.shared.communication import get_service_bus


class CaseServiceWithInterModuleCommunication:
    """
    Example service showing how to communicate with other modules.
    
    This service needs to verify that a user exists before creating a case.
    Instead of directly importing from users module, it uses the service bus.
    """
    
    def __init__(self, case_repository: CaseRepository):
        self._case_repository = case_repository
    
    async def create_case_for_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        title: str,
        primary_incident_id: UUID
    ) -> Case:
        """
        Create a case for a user, verifying user exists first.
        
        This demonstrates inter-module communication through service bus.
        """
        # Get user service through service bus (no direct import!)
        service_bus = get_service_bus()
        
        if not service_bus.has_service("users"):
            raise RuntimeError("Users service not registered in service bus")
        
        user_service = service_bus.get_service("users")
        
        # Verify user exists (this calls users module through public API)
        user = await user_service.get_user_by_id(db, user_id)
        
        # Now create the case
        # (case creation logic would go here)
        
        # This is just an example - actual implementation would create the case
        case = await self._case_repository.get_case_by_id(db, UUID('00000000-0000-0000-0000-000000000000'))
        return case
