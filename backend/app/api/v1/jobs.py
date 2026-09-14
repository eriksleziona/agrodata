"""Jobs API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import (
    CurrentUserDep,
    DBSessionDep,
    WRITER_ROLES,
)
from app.models.job import JobStatus
from app.models.user import User
from app.schemas.job import JobCreate, JobFinish, JobRead
from app.services.jobs import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _check_org(resource_org: UUID, current_user: User) -> None:
    """Raise HTTP 404 if *resource_org* differs from the current user's org."""

    if resource_org != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")


def _require_writer(current_user: User) -> None:
    if current_user.role not in WRITER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of: {', '.join(r.value for r in WRITER_ROLES)}.",
        )


@router.get("", response_model=list[JobRead])
def list_jobs(
    current_user: CurrentUserDep,
    session: DBSessionDep,
    status: JobStatus | None = None,
    machine_id: UUID | None = None,
    operator_id: UUID | None = None,
) -> list[JobRead]:
    """Retrieve all jobs belonging to the authenticated user's organization."""

    jobs = JobService(session).list_all(
        organization_id=current_user.organization_id,
        status=status,
        machine_id=machine_id,
        operator_id=operator_id,
    )
    return [JobRead.model_validate(j) for j in jobs]


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    data: JobCreate,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> JobRead:
    """Create a new agricultural job."""

    _require_writer(current_user)
    scoped = data.model_copy(update={"organization_id": current_user.organization_id})
    job = JobService(session).create(scoped)
    return JobRead.model_validate(job)


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> JobRead:
    """Retrieve a job by ID, scoped to the authenticated organization."""

    job = JobService(session).get_by_id(job_id)
    _check_org(job.organization_id, current_user)
    return JobRead.model_validate(job)


@router.post("/{job_id}/start", response_model=JobRead)
def start_job(
    job_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to STARTED status."""

    _require_writer(current_user)
    service = JobService(session)
    job = service.get_by_id(job_id)
    _check_org(job.organization_id, current_user)
    return JobRead.model_validate(service.start(job_id))


@router.post("/{job_id}/pause", response_model=JobRead)
def pause_job(
    job_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to PAUSED status."""

    _require_writer(current_user)
    service = JobService(session)
    job = service.get_by_id(job_id)
    _check_org(job.organization_id, current_user)
    return JobRead.model_validate(service.pause(job_id))


@router.post("/{job_id}/resume", response_model=JobRead)
def resume_job(
    job_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to STARTED status from PAUSED."""

    _require_writer(current_user)
    service = JobService(session)
    job = service.get_by_id(job_id)
    _check_org(job.organization_id, current_user)
    return JobRead.model_validate(service.resume(job_id))


@router.post("/{job_id}/finish", response_model=JobRead)
def finish_job(
    job_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
    metrics: JobFinish | None = None,
) -> JobRead:
    """Transition a job to COMPLETED status and optionally record summary metrics."""

    _require_writer(current_user)
    service = JobService(session)
    job = service.get_by_id(job_id)
    _check_org(job.organization_id, current_user)
    return JobRead.model_validate(service.finish(job_id, metrics=metrics))


@router.post("/{job_id}/cancel", response_model=JobRead)
def cancel_job(
    job_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> JobRead:
    """Transition a job to CANCELLED status."""

    _require_writer(current_user)
    service = JobService(session)
    job = service.get_by_id(job_id)
    _check_org(job.organization_id, current_user)
    return JobRead.model_validate(service.cancel(job_id))
