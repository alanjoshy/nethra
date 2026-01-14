import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.security import hash_password
from app.models.user import User


ADMIN_EMAIL = "admin@sentinel.local"
ADMIN_PASSWORD = "ChangeMe123!"
ADMIN_NAME = "System Admin"


async def seed_admin():
    async with async_session() as session:
        result = await session.execute(
            User.__table__.select().where(User.email == ADMIN_EMAIL)
        )
        if result.first():
            print("Admin already exists")
            return

        admin = User(
            id=uuid.uuid4(),
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )

        session.add(admin)
        await session.commit()
        print("Admin user created")


if __name__ == "__main__":
    asyncio.run(seed_admin())
