"""Enable the PostGIS extension.

Revision ID: 20260813_0001
Revises:
Create Date: 2026-08-13 00:00:00+00:00
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "20260813_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Enable PostGIS for spatial data support."""

    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def downgrade() -> None:
    """Remove PostGIS while the database contains no spatial application data."""

    op.execute("DROP EXTENSION IF EXISTS postgis")
