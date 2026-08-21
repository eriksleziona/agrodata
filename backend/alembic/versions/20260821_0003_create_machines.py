"""Create machines table.

Revision ID: 20260821_0003
Revises: 20260813_0002
Create Date: 2026-08-21 12:00:00+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260821_0003"
down_revision = "20260813_0002"
branch_labels = None
depends_on = None

utc_timestamp = sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)")


def upgrade() -> None:
    """Create the machines persistence structure."""

    op.create_table(
        "machines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("power_hp", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.String(length=100), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_machines_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_machines"),
        sa.UniqueConstraint("device_id", name="uq_machines_device_id"),
    )
    op.create_index("ix_machines_organization_id", "machines", ["organization_id"])
    op.create_index("ix_machines_device_id", "machines", ["device_id"])


def downgrade() -> None:
    """Remove the machines persistence structure."""

    op.drop_index("ix_machines_device_id", table_name="machines")
    op.drop_index("ix_machines_organization_id", table_name="machines")
    op.drop_table("machines")

