"""Create jobs table and job_status enum.

Revision ID: 20260821_0005
Revises: 20260821_0004
Create Date: 2026-08-21 13:10:00+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260821_0005"
down_revision = "20260821_0004"
branch_labels = None
depends_on = None

job_status = postgresql.ENUM(
    "PLANNED",
    "STARTED",
    "PAUSED",
    "COMPLETED",
    "CANCELLED",
    name="job_status",
    create_type=False,
)
utc_timestamp = sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)")


def upgrade() -> None:
    """Create the jobs persistence structures."""

    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("farm_id", sa.Uuid(), nullable=True),
        sa.Column("field_id", sa.Uuid(), nullable=True),
        sa.Column("machine_id", sa.Uuid(), nullable=True),
        sa.Column("implement_id", sa.Uuid(), nullable=True),
        sa.Column("operator_id", sa.Uuid(), nullable=True),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("status", job_status, server_default="PLANNED", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("area_planned", sa.Float(), nullable=True),
        sa.Column("area_completed", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("distance", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("working_time", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("idle_time", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("fuel_used", sa.Float(), server_default=sa.text("0.0"), nullable=False),
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
            name="fk_jobs_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.id"],
            name="fk_jobs_machine_id_machines",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["implement_id"],
            ["implements.id"],
            name="fk_jobs_implement_id_implements",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["operator_id"],
            ["users.id"],
            name="fk_jobs_operator_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_jobs"),
    )
    op.create_index("ix_jobs_organization_id", "jobs", ["organization_id"])
    op.create_index("ix_jobs_farm_id", "jobs", ["farm_id"])
    op.create_index("ix_jobs_field_id", "jobs", ["field_id"])
    op.create_index("ix_jobs_machine_id", "jobs", ["machine_id"])
    op.create_index("ix_jobs_implement_id", "jobs", ["implement_id"])
    op.create_index("ix_jobs_operator_id", "jobs", ["operator_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])


def downgrade() -> None:
    """Remove the jobs persistence structures."""

    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_operator_id", table_name="jobs")
    op.drop_index("ix_jobs_implement_id", table_name="jobs")
    op.drop_index("ix_jobs_machine_id", table_name="jobs")
    op.drop_index("ix_jobs_field_id", table_name="jobs")
    op.drop_index("ix_jobs_farm_id", table_name="jobs")
    op.drop_index("ix_jobs_organization_id", table_name="jobs")
    op.drop_table("jobs")
    job_status.drop(op.get_bind(), checkfirst=True)

