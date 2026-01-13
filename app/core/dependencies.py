"""
Central location for dependency providers.
Concrete implementations will be added incrementally.
"""
from collections.abc import AsyncGenerator
from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
