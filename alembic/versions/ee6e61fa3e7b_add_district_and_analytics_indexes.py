"""add_district_and_analytics_indexes

Revision ID: ee6e61fa3e7b
Revises: db3834357c68
Create Date: 2026-02-17 00:56:44.691751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee6e61fa3e7b'
down_revision: Union[str, Sequence[str], None] = 'db3834357c68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add district and analytics indexes."""
    # Add optional district column to incidents
    op.add_column('incidents', sa.Column('district', sa.String(100), nullable=True))
    
    # Add index on district for location-based analytics
    op.create_index('ix_incidents_district', 'incidents', ['district'], unique=False)
    
    # Add composite index for case status + date filtering (analytics queries)
    op.create_index(
        'ix_cases_status_created_at',
        'cases',
        ['status', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema - remove district and analytics indexes."""
    op.drop_index('ix_cases_status_created_at', table_name='cases')
    op.drop_index('ix_incidents_district', table_name='incidents')
    op.drop_column('incidents', 'district')
