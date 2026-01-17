import asyncio
import getpass

from sqlalchemy import select

from app.shared.database import AsyncSessionLocal
from app.shared.security import hash_password
from app.modules.users.entities.user_entity import User


async def create_admin():
    email = input("Admin email: ").strip().lower()
    name = input("Admin name: ").strip()
    password = getpass.getpass("Admin password: ")

    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("❌ User with this email already exists.")
            return

        admin_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )

        session.add(admin_user)
        await session.commit()

        print("✅ Admin user created successfully.")


if __name__ == "__main__":
    asyncio.run(create_admin())
