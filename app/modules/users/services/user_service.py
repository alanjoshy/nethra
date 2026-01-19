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
