"""
Database migration utilities for modular monolith.

Each module can have its own migrations directory.
When splitting to microservices, each module's migrations can be moved to its own database.
"""

from pathlib import Path
from alembic.config import Config
from alembic import command

# Base directory for migrations
MIGRATIONS_BASE = Path(__file__).parent.parent.parent.parent / "alembic"


def get_module_migrations_path(module_name: str) -> Path:
    """
    Get the migrations path for a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'users', 'cases')
    
    Returns:
        Path to module's migrations directory
    """
    return MIGRATIONS_BASE / "versions" / module_name


def create_module_migration(module_name: str, message: str) -> None:
    """
    Create a new migration for a specific module.
    
    Args:
        module_name: Name of the module
        message: Migration message
    """
    # This would be integrated with Alembic
    # For now, it's a placeholder showing the concept
    pass
