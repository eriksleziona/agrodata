"""Job input and output schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.job import JobStatus


class JobCreate(BaseModel):
    """Data required to create an agricultural job."""

    organization_id: UUID
    farm_id: UUID | None = None
    field_id: UUID | None = None
    machine_id: UUID | None = None
    implement_id: UUID | None = None
    operator_id: UUID | None = None
    type: str = Field(min_length=1, max_length=100)
    area_planned: float | None = Field(default=None, gt=0)
    status: JobStatus = JobStatus.PLANNED

    @field_validator("type")
    @classmethod
    def strip_required_type(cls, value: str) -> str:
        """Reject blank type after trimming surrounding whitespace."""

        normalized = value.strip()
        if not normalized:
            message = "Value must not be blank."
            raise ValueError(message)
        return normalized


class JobFinish(BaseModel):
    """Optional metrics supplied when completing an agricultural job."""

    area_completed: float | None = Field(default=None, ge=0)
    distance: float | None = Field(default=None, ge=0)
    working_time: int | None = Field(default=None, ge=0)
    idle_time: int | None = Field(default=None, ge=0)
    fuel_used: float | None = Field(default=None, ge=0)


class JobRead(BaseModel):
    """Job data safe to expose to API clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    farm_id: UUID | None
    field_id: UUID | None
    machine_id: UUID | None
    implement_id: UUID | None
    operator_id: UUID | None
    type: str
    status: JobStatus
    started_at: datetime | None
    finished_at: datetime | None
    area_planned: float | None
    area_completed: float
    distance: float
    working_time: int
    idle_time: int
    fuel_used: float
    created_at: datetime
    updated_at: datetime

