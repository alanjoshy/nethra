"""initial schema

Revision ID: d44761de9eeb
Revises: 
Create Date: 2026-01-15 00:12:34.845249
"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d44761de9eeb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS (safe & idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # USERS
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # INCIDENTS
    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("reported_by", sa.UUID(), nullable=False),
        sa.Column("incident_type", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["reported_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Spatial index (idempotent)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'idx_incidents_location'
            ) THEN
                CREATE INDEX idx_incidents_location
                ON incidents USING GIST (location);
            END IF;
        END$$;
        """
    )

    # CASES
    op.create_table(
        "cases",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("primary_incident_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(["primary_incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("primary_incident_id"),
    )

    # CASE STATUS HISTORY
    op.create_table(
        "case_status_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=False),
        sa.Column("new_status", sa.String(length=50), nullable=False),
        sa.Column("changed_by", sa.UUID(), nullable=False),
        sa.Column("changed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # MEDIA
    op.create_table(
        "media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("media_type", sa.String(length=50), nullable=False),
        sa.Column("camera_type", sa.String(length=100), nullable=True),
        sa.Column("capture_time", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop only application-owned objects
    op.drop_table("media")
    op.drop_table("case_status_history")
    op.drop_table("cases")
    op.execute("DROP INDEX IF EXISTS idx_incidents_location")
    op.drop_table("incidents")
    op.drop_table("users")
