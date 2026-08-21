"""Jobs API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import DBSessionDep
from app.models.job import JobStatus
from app.schemas.job import JobCreate, JobFinish, JobRead
from app.services.jobs import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(
    session: DBSessionDep,
    organization_id: UUID | None = None,
    status: JobStatus | None = None,
    machine_id: UUID | None = None,
    operator_id: UUID | None = None,
) -> list[JobRead]:
    """Retrieve all jobs matching optional filter criteria."""

    service = JobService(session)
    jobs = service.list_all(
        organization_id=organization_id,
        status=status,
        machine_id=machine_id,
        operator_id=operator_id,
    )
    return [JobRead.model_validate(j) for j in jobs]


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    data: JobCreate,
    session: DBSessionDep,
) -> JobRead:
    """Create a new agricultural job."""

    service = JobService(session)
    job = service.create(data)
    return JobRead.model_validate(job)


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: UUID,
    session: DBSessionDep,
) -> JobRead:
    """Retrieve a job by its unique identifier."""

    service = JobService(session)
    job = service.get_by_id(job_id)
    return JobRead.model_validate(job)


@router.post("/{job_id}/start", response_model=JobRead)
def start_job(
    job_id: UUID,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to STARTED status."""

    service = JobService(session)
    job = service.start(job_id)
    return JobRead.model_validate(job)


@router.post("/{job_id}/pause", response_model=JobRead)
def pause_job(
    job_id: UUID,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to PAUSED status."""

    service = JobService(session)
    job = service.pause(job_id)
    return JobRead.model_validate(job)


@router.post("/{job_id}/resume", response_model=JobRead)
def resume_job(
    job_id: UUID,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to STARTED status from PAUSED."""

    service = JobService(session)
    job = service.resume(job_id)
    return JobRead.model_validate(job)


@router.post("/{job_id}/finish", response_model=JobRead)
def finish_job(
    job_id: UUID,
    session: DBSessionDep,
    metrics: JobFinish | None = None,
) -> JobRead:
    """Transition a job to COMPLETED status and optionally record summary metrics."""

    service = JobService(session)
    job = service.finish(job_id, metrics=metrics)
    return JobRead.model_validate(job)


@router.post("/{job_id}/cancel", response_model=JobRead)
def cancel_job(
    job_id: UUID,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to CANCELLED status."""

    service = JobService(session)
    job = service.cancel(job_id)
    return JobRead.model_validate(job)

