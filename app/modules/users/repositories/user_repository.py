from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.entities.user_entity import User


class UserRepository:

    @staticmethod
    async def get_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id: str,
    ) -> User | None:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
    ) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def save(db: AsyncSession, user: User) -> User:
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_all(db: AsyncSession) -> list[User]:
        result = await db.execute(select(User))
        return result.scalars().all()
