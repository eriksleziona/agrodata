"""Job persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus


class JobRepository:
    """Database access operations for agricultural jobs."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, job: Job) -> Job:
        """Add a job to the current unit of work."""

        self._session.add(job)
        return job

    def get_by_id(self, job_id: UUID) -> Job | None:
        """Return a job by its UUID, if it exists."""

        return self._session.get(Job, job_id)

    def list_all(
        self,
        organization_id: UUID | None = None,
        status: JobStatus | None = None,
        machine_id: UUID | None = None,
        operator_id: UUID | None = None,
    ) -> list[Job]:
        """Return all jobs matching optional filter criteria."""

        statement = select(Job)
        if organization_id is not None:
            statement = statement.where(Job.organization_id == organization_id)
        if status is not None:
            statement = statement.where(Job.status == status)
        if machine_id is not None:
            statement = statement.where(Job.machine_id == machine_id)
        if operator_id is not None:
            statement = statement.where(Job.operator_id == operator_id)
        statement = statement.order_by(Job.created_at.desc())
        return list(self._session.scalars(statement).all())

    def delete(self, job: Job) -> None:
        """Mark a job for deletion in the current unit of work."""

        self._session.delete(job)

