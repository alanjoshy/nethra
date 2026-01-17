"""
Main application entry point.
Modular monolith architecture - each module is microservice-ready.
"""

import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.dependencies import get_db
from app.core.health import check_database_connection
from app.shared.middleware import (
    nethra_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.shared.exceptions import NethraException

# Import module routers (only public APIs)
from app.modules.auth import auth_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nethra Backend",
    description="Criminal Case Management System API - Modular Monolith",
    version="2.0.0"
)

# Register exception handlers
app.add_exception_handler(NethraException, nethra_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include module routers
app.include_router(auth_router)


@app.on_event("startup")
async def on_startup():
    try:
        async for db in get_db():
            await check_database_connection(db)
            logger.info("✅ Database connection verified")
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
