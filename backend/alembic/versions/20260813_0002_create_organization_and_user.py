"""Create organization and user tables.

Revision ID: 20260813_0002
Revises: 20260813_0001
Create Date: 2026-08-13 00:00:01+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260813_0002"
down_revision = "20260813_0001"
branch_labels = None
depends_on = None


user_role = postgresql.ENUM(
    "OWNER",
    "ADMIN",
    "OPERATOR",
    "FARMER",
    "VIEWER",
    name="user_role",
    create_type=False,
)
utc_timestamp = sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)")


def upgrade() -> None:
    """Create the initial organization and user persistence structures."""

    user_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=64), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_organizations"),
    )
    op.create_index("ix_organizations_tax_id", "organizations", ["tax_id"])

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=1024), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("role", user_role, nullable=False),
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
            name="fk_users_organization_id_organizations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint(
            "organization_id",
            "email",
            name="uq_users_organization_id_email",
        ),
    )
    op.create_index("ix_users_organization_id", "users", ["organization_id"])


def downgrade() -> None:
    """Remove the initial organization and user persistence structures."""

    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_organizations_tax_id", table_name="organizations")
    op.drop_table("organizations")
    user_role.drop(op.get_bind(), checkfirst=True)
