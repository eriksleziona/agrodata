"""Create implements table.

Revision ID: 20260821_0004
Revises: 20260821_0003
Create Date: 2026-08-21 13:00:00+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260821_0004"
down_revision = "20260821_0003"
branch_labels = None
depends_on = None

utc_timestamp = sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)")


def upgrade() -> None:
    """Create the implements persistence structure."""

    op.create_table(
        "implements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("type", sa.String(length=100), nullable=True),
        sa.Column("working_width", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=utc_timestamp,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=utc_timestamp,
            nullable=False,
        ),
        sa.CheckConstraint("working_width > 0", name="ck_implements_working_width_positive"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_implements_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_implements"),
    )
    op.create_index("ix_implements_organization_id", "implements", ["organization_id"])


def downgrade() -> None:
    """Remove the implements persistence structure."""

    op.drop_index("ix_implements_organization_id", table_name="implements")
    op.drop_table("implements")

