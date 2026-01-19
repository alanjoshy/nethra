from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.entities.user_entity import User


class AuthUserRepository:
    """
    Repository for authentication-specific user queries.
    Maintains isolation from the general UserRepository.
    """

    @staticmethod
    async def get_active_user_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:
        """
        Retrieve an active user by email address.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            User object if found and active, None otherwise
        """
        result = await db.execute(
            select(User).where(
                User.email == email,
                User.is_active == True
            )
        )
        return result.scalar_one_or_none()
