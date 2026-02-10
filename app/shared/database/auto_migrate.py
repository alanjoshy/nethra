"""
Auto-migration utility for development.

On server startup, auto-detects model changes and generates + applies
Alembic migrations. Only runs when AUTO_MIGRATE=true and ENVIRONMENT=development.
"""

import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.autogenerate import compare_metadata
from sqlalchemy import create_engine, pool

from app.core.config import settings

# Import Base with all models registered
from app.shared.database import Base  # noqa: F401
import app.shared.database.models  # noqa: F401

logger = logging.getLogger(__name__)

# Project root (where alembic.ini lives)
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _get_sync_url() -> str:
    """
    Convert the async DATABASE_URL to a sync one for Alembic.
    asyncpg -> psycopg2, and append sslmode=require for Supabase.
    """
    url = settings.database_url.strip()
    url = url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    # Ensure SSL for Supabase
    if "sslmode" not in url:
        separator = "&" if "?" in url else "?"
        url += f"{separator}sslmode=require"
    return url


def _get_alembic_config() -> Config:
    """Build an Alembic Config pointing at the project root."""
    ini_path = str(PROJECT_ROOT / "alembic.ini")
    cfg = Config(ini_path)
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", _get_sync_url())
    return cfg


def _has_pending_changes(cfg: Config) -> bool:
    """
    Compare current models against the latest migration head
    to check if there are schema differences.
    """
    sync_url = _get_sync_url()
    engine = create_engine(sync_url, poolclass=pool.NullPool)

    try:
        with engine.connect() as connection:
            from alembic.migration import MigrationContext

            mc = MigrationContext.configure(connection)
            diff = compare_metadata(mc, Base.metadata)
            return len(diff) > 0
    finally:
        engine.dispose()


def run_auto_migrate() -> None:
    """
    Auto-detect model changes and generate + apply migrations.

    This function is safe to call on every startup:
    - If no changes are detected, it does nothing.
    - If changes exist, it generates a migration and upgrades.
    - Errors are caught and logged; the server still starts.
    """
    logger.info("🔄 Auto-migration: checking for schema changes...")

    try:
        cfg = _get_alembic_config()

        # First, ensure we're at the latest migration head
        command.upgrade(cfg, "head")

        # Check if models have diverged from DB
        if not _has_pending_changes(cfg):
            logger.info("✅ Auto-migration: no schema changes detected")
            return

        # Generate a new migration
        logger.info("📝 Auto-migration: generating new migration...")
        command.revision(
            cfg,
            message="auto-generated migration",
            autogenerate=True,
        )

        # Apply the new migration
        logger.info("⬆️  Auto-migration: applying migration...")
        command.upgrade(cfg, "head")

        logger.info("✅ Auto-migration: complete")

    except Exception as exc:
        logger.error(
            f"⚠️  Auto-migration failed (non-fatal): {exc}",
            exc_info=True,
        )
