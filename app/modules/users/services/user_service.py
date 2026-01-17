"""
User service - Business logic for user management.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.entities.user_entity import User
from app.modules.users.repositories.user_repository import UserRepository
from app.shared.exceptions import NotFoundError


class UserService:
    """
    User service.
    Handles business logic for user operations.
    """
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> User:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            User object
        
        Raises:
            NotFoundError: If user not found
        """
        user = await self._user_repository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundError(resource="User", identifier=user_id)
        return user
    
    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            User object or None
        """
        return await self._user_repository.get_user_by_email(db, email)
    
    async def get_active_user_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """
        Get an active user by email.
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            Active User object or None
        """
        return await self._user_repository.get_active_user_by_email(db, email)
