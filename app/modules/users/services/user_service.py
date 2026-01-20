from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.entities.user_entity import User
from app.modules.users.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.common.exceptions import ConflictError


class UserService:

    @staticmethod
    async def create_user(
        *,
        db: AsyncSession,
        name: str,
        email: str,
        password: str,
        role: str,
    ) -> User:
        existing = await UserRepository.get_by_email(db, email)
        if existing:
            raise ConflictError("User with this email already exists")

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
        )

        return await UserRepository.create(db, user)

    @staticmethod
    async def list_users(db: AsyncSession) -> list[User]:
        return await UserRepository.get_all(db)

    @staticmethod
    async def get_user(db: AsyncSession, user_id) -> User:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User not found")
        return user 

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id,
        name: str | None,
        role: str | None,
        is_active: bool | None,
    ) -> User:
        user = await UserService.get_user(db, user_id)

        if name is not None:
            user.name = name
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        return await UserRepository.save(db, user)

    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id) -> User:
        user = await UserService.get_user(db, user_id)
        user.is_active = False
        return await UserRepository.save(db, user)

