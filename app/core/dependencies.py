"""
Central location for dependency providers.
Concrete implementations will be added incrementally.
"""
from collections.abc import AsyncGenerator
from app.core.database import AsyncSessionLocal
from fastapi import Depends, HTTPException, Header
from app.core.security import decode_token 


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token") 