"""Job application service and state machine transitions."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.job import Job, JobStatus
from app.repositories.implements import ImplementRepository
from app.repositories.jobs import JobRepository
from app.repositories.machines import MachineRepository
from app.repositories.organizations import OrganizationRepository
from app.repositories.users import UserRepository
from app.schemas.job import JobCreate, JobFinish
from app.services.errors import (
    ImplementNotFoundError,
    InvalidJobStateTransitionError,
    JobNotFoundError,
    MachineNotFoundError,
    OrganizationNotFoundError,
)


class JobService:
    """Coordinates agricultural job lifecycle and state transitions."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._organizations = OrganizationRepository(session)
        self._machines = MachineRepository(session)
        self._implements = ImplementRepository(session)
        self._users = UserRepository(session)
        self._jobs = JobRepository(session)

    def create(self, data: JobCreate) -> Job:
        """Create and persist a new agricultural job after validating references."""

        if self._organizations.get_by_id(data.organization_id) is None:
            raise OrganizationNotFoundError(
                f"Organization {data.organization_id} was not found."
            )

        if data.machine_id is not None:
            machine = self._machines.get_by_id(data.machine_id)
            if machine is None or machine.organization_id != data.organization_id:
                raise MachineNotFoundError(
                    f"Machine {data.machine_id} was not found in organization {data.organization_id}."
                )

        if data.implement_id is not None:
            implement = self._implements.get_by_id(data.implement_id)
            if implement is None or implement.organization_id != data.organization_id:
                raise ImplementNotFoundError(
                    f"Implement {data.implement_id} was not found in organization {data.organization_id}."
                )

        if data.operator_id is not None:
            user = self._users.get_by_id(data.operator_id)
            if user is None or user.organization_id != data.organization_id:
                raise OrganizationNotFoundError(
                    f"Operator {data.operator_id} was not found in organization {data.organization_id}."
                )

        started_at = utc_now() if data.status == JobStatus.STARTED else None

        job = self._jobs.add(
            Job(
                organization_id=data.organization_id,
                farm_id=data.farm_id,
                field_id=data.field_id,
                machine_id=data.machine_id,
                implement_id=data.implement_id,
                operator_id=data.operator_id,
                type=data.type,
                status=data.status,
                started_at=started_at,
                area_planned=data.area_planned,
            )
        )
        self._commit_and_refresh(job)
        return job

    def get_by_id(self, job_id: UUID) -> Job:
        """Return a job by its UUID or raise JobNotFoundError."""

        job = self._jobs.get_by_id(job_id)
        if job is None:
            raise JobNotFoundError(f"Job {job_id} was not found.")
        return job

    def list_all(
        self,
        organization_id: UUID | None = None,
        status: JobStatus | None = None,
        machine_id: UUID | None = None,
        operator_id: UUID | None = None,
    ) -> list[Job]:
        """Return all jobs matching optional criteria."""

        if (
            organization_id is not None
            and self._organizations.get_by_id(organization_id) is None
        ):
            raise OrganizationNotFoundError(
                f"Organization {organization_id} was not found."
            )

        return self._jobs.list_all(
            organization_id=organization_id,
            status=status,
            machine_id=machine_id,
            operator_id=operator_id,
        )

    def start(self, job_id: UUID) -> Job:
        """Transition a job from PLANNED to STARTED."""

        job = self.get_by_id(job_id)
        if job.status != JobStatus.PLANNED:
            raise InvalidJobStateTransitionError(
                f"Cannot start a job with status '{job.status.value}'. Job must be in '{JobStatus.PLANNED.value}' status."
            )

        job.status = JobStatus.STARTED
        if job.started_at is None:
            job.started_at = utc_now()

        self._commit_and_refresh(job)
        return job

    def pause(self, job_id: UUID) -> Job:
        """Transition a job from STARTED to PAUSED."""

        job = self.get_by_id(job_id)
        if job.status != JobStatus.STARTED:
            raise InvalidJobStateTransitionError(
                f"Cannot pause a job with status '{job.status.value}'. Job must be in '{JobStatus.STARTED.value}' status."
            )

        job.status = JobStatus.PAUSED
        self._commit_and_refresh(job)
        return job

    def resume(self, job_id: UUID) -> Job:
        """Transition a job from PAUSED to STARTED."""

        job = self.get_by_id(job_id)
        if job.status != JobStatus.PAUSED:
            raise InvalidJobStateTransitionError(
                f"Cannot resume a job with status '{job.status.value}'. Job must be in '{JobStatus.PAUSED.value}' status."
            )

        job.status = JobStatus.STARTED
        self._commit_and_refresh(job)
        return job

    def finish(self, job_id: UUID, metrics: JobFinish | None = None) -> Job:
        """Transition a job from STARTED or PAUSED to COMPLETED."""

        job = self.get_by_id(job_id)
        if job.status not in (JobStatus.STARTED, JobStatus.PAUSED):
            raise InvalidJobStateTransitionError(
                f"Cannot finish a job with status '{job.status.value}'. Job must be in '{JobStatus.STARTED.value}' or '{JobStatus.PAUSED.value}' status."
            )

        job.status = JobStatus.COMPLETED
        job.finished_at = utc_now()

        if metrics is not None:
            if metrics.area_completed is not None:
                job.area_completed = metrics.area_completed
            if metrics.distance is not None:
                job.distance = metrics.distance
            if metrics.working_time is not None:
                job.working_time = metrics.working_time
            if metrics.idle_time is not None:
                job.idle_time = metrics.idle_time
            if metrics.fuel_used is not None:
                job.fuel_used = metrics.fuel_used

        self._commit_and_refresh(job)
        return job

    def cancel(self, job_id: UUID) -> Job:
        """Transition a job from PLANNED, STARTED, or PAUSED to CANCELLED."""

        job = self.get_by_id(job_id)
        if job.status in (JobStatus.COMPLETED, JobStatus.CANCELLED):
            raise InvalidJobStateTransitionError(
                f"Cannot cancel a job with status '{job.status.value}'. Job is already in a terminal state."
            )

        job.status = JobStatus.CANCELLED
        if job.finished_at is None:
            job.finished_at = utc_now()

        self._commit_and_refresh(job)
        return job

    def _commit_and_refresh(self, job: Job) -> None:
        """Commit the current unit of work and refresh model attributes."""

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        self._session.refresh(job)

