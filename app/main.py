import logging

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_db
from app.core.health import check_database_connection

logger = logging.getLogger(__name__)

app = FastAPI(title="Nethra Backend")


@app.on_event("startup")
async def on_startup():
    try:
        async for db in get_db():
            await check_database_connection(db)
    except Exception as exc:
        # IMPORTANT: do NOT crash the app
        logger.error(f"Startup DB check failed (non-fatal): {exc}")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/db")
async def db_health(db: AsyncSession = Depends(get_db)):
    try:
        await check_database_connection(db)
        return {"status": "database connected"}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="database not reachable",
        )
