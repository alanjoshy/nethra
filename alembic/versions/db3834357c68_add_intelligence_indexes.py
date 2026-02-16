"""add_intelligence_indexes

Revision ID: db3834357c68
Revises: b9ebb83671e1
Create Date: 2026-02-17 00:36:28.701045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db3834357c68'
down_revision: Union[str, Sequence[str], None] = 'b9ebb83671e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add intelligence indexes."""
    # Index on incident_tags.tag_id for tag filtering
    op.create_index(
        'ix_incident_tags_tag_id',
        'incident_tags',
        ['tag_id'],
        unique=False
    )
    
    # Index on case_persons.person_id for suspect lookups
    op.create_index(
        'ix_case_persons_person_id',
        'case_persons',
        ['person_id'],
        unique=False
    )
    
    # Index on incidents.occurred_at for temporal queries
    op.create_index(
        'ix_incidents_occurred_at',
        'incidents',
        ['occurred_at'],
        unique=False
    )
    
    # Note: Spatial index on incidents.location already exists from initial migration


def downgrade() -> None:
    """Downgrade schema - remove intelligence indexes."""
    op.drop_index('ix_incidents_occurred_at', table_name='incidents')
    op.drop_index('ix_case_persons_person_id', table_name='case_persons')
    op.drop_index('ix_incident_tags_tag_id', table_name='incident_tags')
