"""
User repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.entities.user_entity import User


class UserRepository:
    """
    Repository for User entity.
    Handles all database operations for users.
    """
    
    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """
        Get a user by their email address.
        
        Args:
            db: Database session
            email: User email address
        
        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_user_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """
        Get an active user by their email address.
        
        Args:
            db: Database session
            email: User email address
        
        Returns:
            Active User object if found, None otherwise
        """
        result = await db.execute(
            select(User).where(
                User.email == email, 
                User.is_active == True
            )
        )
        return result.scalar_one_or_none()
