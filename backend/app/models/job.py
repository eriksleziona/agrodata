"""Job persistence model and supported job statuses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.implement import Implement
    from app.models.machine import Machine
    from app.models.organization import Organization
    from app.models.user import User


class JobStatus(str, Enum):
    """Lifecycle statuses for agricultural operations."""

    PLANNED = "PLANNED"
    STARTED = "STARTED"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Job(Base):
    """An organization-scoped agricultural work operation or service."""

    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    farm_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        index=True,
    )
    field_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        index=True,
    )
    machine_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("machines.id"),
        nullable=True,
        index=True,
    )
    implement_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("implements.id"),
        nullable=True,
        index=True,
    )
    operator_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        SqlEnum(JobStatus, name="job_status", validate_strings=True),
        nullable=False,
        default=JobStatus.PLANNED,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    area_planned: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_completed: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    distance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    working_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    idle_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    fuel_used: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    organization: Mapped[Organization] = relationship(back_populates="jobs")
    machine: Mapped[Machine | None] = relationship()
    implement: Mapped[Implement | None] = relationship()
    operator: Mapped[User | None] = relationship()

